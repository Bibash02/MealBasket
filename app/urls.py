from django.urls import path
from .views import *

urlpatterns = [
    path('home', home, name='home1'),
    path('auth', auth, name='auth'),
    path('', test, name='home'),

    path('signup', signup_view, name='signup'),
    path('signin/', signin_view, name='signin'),
    path('logout', logout_view, name='logout'),

    path('customer/dashboard', customer_dashboard, name='customer_dashboard'),
    path('vendor/dashboard', vender_dashboard, name='vendor_dashboard'),

    path('customer/update/profile', update_customer_profile, name='update_customer_profile'),
    path('customer/add-to-cart/<int:product_id>/', add_to_cart, name='add_to_cart'),
    path('customer/cart', view_cart, name='view_cart'),
    path('customer/cart/update/<int:item_id>/', update_cart_item, name='update_cart_item'),
    path('customer/cart/remove/<int:item_id>/', remove_cart_item, name='remove_cart_item'),

    path('customer/checkout', checkout, name='checkout'),
    path('customer/payment/<int:order_id>/', process_payment, name='process_payment'),
    path('customer/payment/success', payment_success, name='payment_success'),
    path('customer/payment/cancel', payment_failed, name='payment_failed'),

    path('vendor/save-product', save_product, name='save_product'),
    path('vendor/product/list', my_products, name='vendor_product_list'),
    path('vendor/product/add', add_product, name='add_product'),
    path('vendor/product/edit/<int:product_id>/', edit_product, name='edit_product'),
    path('vendor/product/delete/<int:product_id>/', delete_product, name='delete_product'),
    path('vendor/profile', update_vendor_profile, name='update_vendor_profile'),
]