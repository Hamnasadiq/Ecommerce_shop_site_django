from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.core.paginator import Paginator
from django.db import transaction

from .models import (
    Products,
    Category,
    SubCategory,
    Cart,
    CartItem,
    Order,
    OrderItem,
    Wishlist,
)


# ==========================
# INDEX (PRODUCT LISTING)
# ==========================
def index(request):

    product_objects = Products.objects.all()

    # CATEGORY FILTER
    category_id = request.GET.get("category")
    if category_id:
        product_objects = product_objects.filter(category_id=category_id)

    # SUBCATEGORY FILTER
    subcategory_id = request.GET.get("subcategory")
    if subcategory_id:
        product_objects = product_objects.filter(subcategory_id=subcategory_id)

    # SEARCH
    item_name = request.GET.get("item_name")
    if item_name:
        product_objects = product_objects.filter(title__icontains=item_name)

    # PAGINATION
    paginator = Paginator(product_objects, 10)
    page = request.GET.get("page")
    product_objects = paginator.get_page(page)

    # Categories with prefetch
    categories = Category.objects.prefetch_related("subcategories")

    # Wishlist IDs for heart icon state
    wishlist_ids = []
    if request.user.is_authenticated:
        wishlist, _ = Wishlist.objects.get_or_create(user=request.user)
        wishlist_ids = list(wishlist.products.values_list("id", flat=True))

    context = {
        "product_objects": product_objects,
        "categories": categories,
        "wishlist_ids": wishlist_ids,
    }

    return render(request, "shop/index.html", context)


# ==========================
# PRODUCT DETAIL
# ==========================
def details(request, id):
    product_object = get_object_or_404(Products, id=id)
    return render(request, "shop/details.html", {"product_object": product_object})


# ==========================
# ADD TO CART  (server-side)
# ==========================
@login_required
def add_to_cart(request, product_id):
    """Add a product to the authenticated user's cart."""
    product = get_object_or_404(Products, id=product_id)
    cart, _ = Cart.objects.get_or_create(user=request.user)

    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product,
        defaults={"price": product.price, "quantity": 1},
    )

    if not created:
        cart_item.quantity += 1
        cart_item.save()

    messages.success(request, f"{product.title} added to cart!")
    # Redirect back to wherever the user came from
    return redirect(request.META.get("HTTP_REFERER", "/"))


# ==========================
# CART VIEW
# ==========================
@login_required
def cart_view(request):
    """Display the user's cart with items, summary, and order-tracking form."""
    cart, _ = Cart.objects.get_or_create(user=request.user)
    cart_items = cart.items.select_related("product").all()

    context = {
        "cart": cart,
        "cart_items": cart_items,
    }
    return render(request, "shop/cart.html", context)


# ==========================
# DELETE CART ITEM
# ==========================
@login_required
def delete_cart_item(request, item_id):
    """Remove a single item from the user's cart (owner-only)."""
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    product_name = cart_item.product.title
    cart_item.delete()
    messages.success(request, f"{product_name} removed from cart.")
    return redirect("cart")


# ==========================
# PLACE ORDER  (atomic)
# ==========================
@login_required
def place_order(request):
    """
    Convert the user's cart into an Order + OrderItems.
    Uses a database transaction so partial saves never happen.
    """
    cart = get_object_or_404(Cart, user=request.user)
    cart_items = cart.items.select_related("product").all()

    if not cart_items.exists():
        messages.warning(request, "Your cart is empty — add items first!")
        return redirect("cart")

    with transaction.atomic():
        # 1. Create Order
        order = Order.objects.create(
            user=request.user,
            total=cart.total_price,
        )

        # 2. Move CartItems → OrderItems
        order_items = [
            OrderItem(
                order=order,
                product_name=item.product.title,
                price=item.price,
                quantity=item.quantity,
            )
            for item in cart_items
        ]
        OrderItem.objects.bulk_create(order_items)

        # 3. Clear the cart
        cart_items.delete()

    return redirect("order_success", order_code=order.order_code)


# ==========================
# ORDER SUCCESS PAGE
# ==========================
@login_required
def order_success(request, order_code):
    """Display animated success page with the order code."""
    order = get_object_or_404(Order, order_code=order_code, user=request.user)
    return render(request, "shop/order_success.html", {"order": order})


# ==========================
# TRACK ORDER
# ==========================
@login_required
def track_order(request):
    """
    Accept an order code via POST, validate ownership,
    and display the order's items.
    """
    order = None
    error = None

    if request.method == "POST":
        code = request.POST.get("order_code", "").strip()

        if not code:
            error = "Please enter an order code."
        else:
            try:
                order = Order.objects.prefetch_related("items").get(
                    order_code=code, user=request.user
                )
            except Order.DoesNotExist:
                error = "Invalid order code or this order doesn't belong to you."

    return render(
        request,
        "shop/order_track_result.html",
        {"order": order, "error": error},
    )


# ==========================
# PROFILE PAGE
# ==========================
@login_required
def profile_view(request):
    """Display user profile with username, email, and wishlist."""
    wishlist, _ = Wishlist.objects.get_or_create(user=request.user)
    wishlist_items = wishlist.products.all()

    context = {
        "wishlist_items": wishlist_items,
    }
    return render(request, "shop/profile.html", context)


# ==========================
# TOGGLE WISHLIST
# ==========================
@login_required
def toggle_wishlist(request, product_id):
    """Add or remove a product from the user's wishlist."""
    product = get_object_or_404(Products, id=product_id)
    wishlist, _ = Wishlist.objects.get_or_create(user=request.user)

    if wishlist.products.filter(id=product_id).exists():
        wishlist.products.remove(product)
        messages.success(request, f"{product.title} removed from wishlist.")
    else:
        wishlist.products.add(product)
        messages.success(request, f"{product.title} added to wishlist!")

    return redirect(request.META.get("HTTP_REFERER", "/"))


# ==========================
# CHECKOUT (legacy kept for reference)
# ==========================
def checkout(request):
    """Legacy checkout — now redirects to the new server-side cart."""
    return redirect("cart")


# ==========================
# AUTHENTICATION VIEWS
# ==========================
def signup_view(request):

    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists")
            return redirect("signup")

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
        )
        user.save()
        login(request, user)
        return redirect("/")

    return render(request, "shop/signup.html")


def login_view(request):

    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect("/")
        else:
            messages.error(request, "Invalid Login")
            return redirect("login")

    return render(request, "shop/login.html")


def logout_view(request):
    logout(request)
    return redirect("/")
