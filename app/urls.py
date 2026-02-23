from django.urls import path
from .views import *

urlpatterns = [
    path('home', home, name='home1'),
    path('auth', auth, name='auth'),
    path('', test, name='home'),

    path('signup_post/', signup_post, name='signup'),
    path('signin_post/', signin_post, name='signin'),
    path('logout', logout_view, name='logout'),

    path('customer/dashboard', customer_dashboard, name='customer_dashboard'),
    path('vendor/dashboard', vender_dashboard, name='vendor_dashboard'),

    path('vendor/save-product', save_product, name='save_product'),
    path('vendor/product/edit/<int:product_id>/', edit_product, name='edit_product'),
    path('vendor/product/delete/<int:product_id>/', delete_product, name='delete_product'),
    path('vendor/profile', save_vendor_profile, name='vendor_profile'),
]