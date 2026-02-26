"""
URL configuration for ecomsite project.
"""
from django.contrib import admin
from django.urls import path, include
from shop import views


urlpatterns = [

    path('admin/', admin.site.urls),

    path('chaining/', include('smart_selects.urls')),

    # pages
    path('', views.index, name='index'),

    path('<int:id>/', views.details, name='details'),

    # cart (server-side)
    path('cart/', views.cart_view, name='cart'),

    path('add-to-cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),

    path('delete-cart-item/<int:item_id>/', views.delete_cart_item, name='delete_cart_item'),

    # orders
    path('place-order/', views.place_order, name='place_order'),

    path('order-success/<str:order_code>/', views.order_success, name='order_success'),

    path('track-order/', views.track_order, name='track_order'),

    # legacy checkout redirect
    path('checkout/', views.checkout, name='checkout'),

    # authentication
    path('signup/', views.signup_view, name='signup'),

    path('login/', views.login_view, name='login'),

    path('logout/', views.logout_view, name='logout'),

    # profile & wishlist
    path('profile/', views.profile_view, name='profile'),
    path('wishlist/toggle/<int:product_id>/', views.toggle_wishlist, name='toggle_wishlist'),

]