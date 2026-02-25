from django.shortcuts import render
from .models import Products,Order
from django.core.paginator import Paginator
from django.shortcuts import render,redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate,login,logout
from django.contrib import messages
# Create your views here.

from .models import  Category, SubCategory



def index(request):

    product_objects = Products.objects.all()

    # ======================
    # CATEGORY FILTER
    # ======================

    category_id = request.GET.get("category")

    if category_id:
        product_objects = product_objects.filter(
            category_id=category_id
        )


    # ======================
    # SUBCATEGORY FILTER
    # ======================

    subcategory_id = request.GET.get("subcategory")

    if subcategory_id:
        product_objects = product_objects.filter(
            subcategory_id=subcategory_id
        )


    # ======================
    # SEARCH
    # ======================

    item_name = request.GET.get('item_name')

    if item_name:
        product_objects = product_objects.filter(
            title__icontains=item_name
        )


    # ======================
    # PAGINATION
    # ======================

    paginator = Paginator(product_objects,4)

    page = request.GET.get('page')

    product_objects = paginator.get_page(page)


    # send categories
    categories = Category.objects.prefetch_related(
        "subcategories"
    )


    context = {

        'product_objects':product_objects,

        'categories':categories

    }

    return render(request,'shop/index.html',context)
# detail page view

def details(request,id):
    product_object=Products.objects.get(id=id)
    return render(request,'shop/details.html',{'product_object':product_object})



# checkout view
 
def checkout(request):
    if request.method=="POST":
        items=request.POST.get('items','')
        name=request.POST.get('name',"")
        email=request.POST.get('email',"")
        address=request.POST.get('address',"")
        city=request.POST.get('city',"")
        state=request.POST.get('state',"")
        zipcode=request.POST.get('zipcode',"")
        total =request.POST.get('total',"")
        order=Order(items=items,name=name,email=email,address=address,city=city,state=state,zipcode=zipcode,total=total)
        order.save()

    return render(request,'shop/checkout.html')





# signup 
def signup_view(request):

    if request.method == "POST":

        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')

        if User.objects.filter(username=username).exists():

            messages.error(request,"Username already exists")

            return redirect("signup")

        user = User.objects.create_user(

            username=username,
            email=email,
            password=password

        )

        user.save()

        login(request,user)

        return redirect("/")

    return render(request,'shop/signup.html')



# login view

def login_view(request):

    if request.method == "POST":

        username=request.POST.get('username')

        password=request.POST.get('password')

        user=authenticate(

            request,
            username=username,
            password=password
        )

        if user is not None:

            login(request,user)

            return redirect("/")

        else:

            messages.error(request,"Invalid Login")

            return redirect("login")

    return render(request,'shop/login.html')



# logout view
def logout_view(request):

    logout(request)

    return redirect("/")


