import string
import random

from django.conf import settings
from django.db import models
from smart_selects.db_fields import ChainedForeignKey


# ==========================
# CATEGORY MODEL
# ==========================
class Category(models.Model):

    name = models.CharField(max_length=200, unique=True)

    def __str__(self):
        return self.name


# ==========================
# SUB CATEGORY MODEL
# ==========================
class SubCategory(models.Model):

    name = models.CharField(max_length=200)

    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name="subcategories"
    )

    def __str__(self):
        return f"{self.category.name} → {self.name}"


# ==========================
# PRODUCTS MODEL
# ==========================
class Products(models.Model):

    title = models.CharField(max_length=200)

    price = models.FloatField()

    discount = models.FloatField(default=0)

    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    subcategory = ChainedForeignKey(
        SubCategory,
        chained_field="category",
        chained_model_field="category",
        show_all=False,
        auto_choose=True,
        sort=True,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    description = models.TextField()

    # Upload image (optional)
    image = models.ImageField(
        upload_to="products/",
        null=True,
        blank=True
    )

    # Image URL (optional)
    image_url = models.URLField(
        max_length=1000,
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


# ==========================
# WISHLIST MODEL
# ==========================
class Wishlist(models.Model):

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="wishlist"
    )

    products = models.ManyToManyField(
        Products,
        blank=True,
        related_name="wishlisted_by"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Wishlist – {self.user.username}"


# ==========================
# CART MODEL  (one per user)
# ==========================
class Cart(models.Model):

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="cart"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Cart – {self.user.username}"

    @property
    def total_price(self):
        """Sum of (price × quantity) for every item in the cart."""
        return sum(item.line_total for item in self.items.all())

    @property
    def total_items(self):
        return self.items.count()


# ==========================
# CART ITEM MODEL
# ==========================
class CartItem(models.Model):

    cart = models.ForeignKey(
        Cart,
        on_delete=models.CASCADE,
        related_name="items"
    )

    product = models.ForeignKey(
        Products,
        on_delete=models.CASCADE
    )

    quantity = models.PositiveIntegerField(default=1)

    # Price snapshot at time of adding
    price = models.FloatField(
        help_text="Price snapshot captured when the item was added."
    )

    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("cart", "product")

    def __str__(self):
        return f"{self.quantity}× {self.product.title}"

    @property
    def line_total(self):
        return self.price * self.quantity


# ==========================
# ORDER MODEL
# ==========================
def generate_order_code():
    """
    Generate a unique, human-readable order code like #ORD-7A2B9.
    Uses a 5-character alphanumeric string (uppercase + digits).
    Collision-safe: checks database uniqueness before returning.
    """
    chars = string.ascii_uppercase + string.digits
    while True:
        code = "#ORD-" + "".join(random.choices(chars, k=5))
        if not Order.objects.filter(order_code=code).exists():
            return code


class Order(models.Model):

    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("processing", "Processing"),
        ("shipped", "Shipped"),
        ("delivered", "Delivered"),
        ("cancelled", "Cancelled"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="orders"
    )

    order_code = models.CharField(
        max_length=20,
        unique=True,
        editable=False,
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending"
    )

    total = models.FloatField()

    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.order_code:
            self.order_code = generate_order_code()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.order_code} – {self.user.username} (${self.total:.2f})"


# ==========================
# ORDER ITEM MODEL
# ==========================
class OrderItem(models.Model):

    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="items"
    )

    product_name = models.CharField(max_length=200)
    price = models.FloatField()
    quantity = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.quantity}× {self.product_name}"

    @property
    def line_total(self):
        return self.price * self.quantity