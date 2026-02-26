from django.contrib import admin
from .models import Products, Category, SubCategory, Cart, CartItem, Order, OrderItem


# Register your models here.

admin.site.register(Products)
admin.site.register(Category)
admin.site.register(SubCategory)


class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0
    readonly_fields = ("product", "quantity", "price")


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ("user", "total_items", "total_price", "updated_at")
    inlines = [CartItemInline]


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ("product_name", "quantity", "price")


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("order_code", "user", "total", "status", "created_at")
    list_filter = ("status",)
    search_fields = ("order_code", "user__username")
    readonly_fields = ("order_code",)
    inlines = [OrderItemInline]
