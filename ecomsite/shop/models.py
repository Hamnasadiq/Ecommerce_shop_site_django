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
# ORDER MODEL
# ==========================
class Order(models.Model):

    items = models.TextField()

    name = models.CharField(max_length=200)

    email = models.EmailField()

    address = models.CharField(max_length=1000)

    city = models.CharField(max_length=200)

    state = models.CharField(max_length=200)

    zipcode = models.CharField(max_length=20)

    total = models.FloatField()

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order - {self.name} ({self.total})"