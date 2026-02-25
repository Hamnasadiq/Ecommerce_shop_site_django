import os
import django

os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE",
    "ecomsite.settings"   # your project name
)

django.setup()

from shop.models import Category, SubCategory


data = {

    "Electronics & Gadgets": [
        "Mobiles","Laptops","Tablets",
        "Audio","Cameras","Gaming"
    ],

    "Fashion": [
        "Men","Women","Kids",
        "Sportswear","Accessories"
    ],

    "Home & Living": [
        "Furniture","Decor",
        "Kitchen","Lighting"
    ],

    "Beauty & Care": [
        "Skincare","Haircare",
        "Makeup","Fragrances"
    ],

    "Sports & Outdoors": [
        "Fitness","Cycling",
        "Sports Gear","Gym Equipment"
    ],

    "Books, Music & Media": [
        "Books","E-books",
        "Music","Movies","Games"
    ],

    "Automotive & Tools": [
        "Car Accessories",
        "Bike Accessories",
        "Tools",
        "Car Care"
    ],

    "Pet Supplies": [
        "Food",
        "Accessories",
        "Toys"
    ],

    "Others":[]
}



for cat, subs in data.items():

    category, created = Category.objects.get_or_create(
        name=cat
    )

    for sub in subs:

        SubCategory.objects.get_or_create(
            name=sub,
            category=category
        )


print("DONE SUCCESSFULLY ✅")
