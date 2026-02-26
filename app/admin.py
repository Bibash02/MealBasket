from django.contrib import admin
from .models import *

# Register your models here.
@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'role', 'user')
    search_fields = ('full_name', 'role', 'user__username')

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'image', 'is_active', 'created_at')
    search_fields = ('name',)
    list_filter = ('is_active', 'created_at')

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'vendor', 'category', 'price', 'stock', 'created_at')
    search_fields = ('name', 'vendor__full_name', 'category__name')
    list_filter = ('created_at',)

@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('customer', 'product', 'quantity', 'added_at')
    search_fields = ('customer__full_name', 'product__name')
    list_filter = ('added_at',)

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display  = ['user', 'full_name', 'email', 'phone', 'address', 'city', 'country', 'amount', 'payment_type', 'transaction_uuid', 'status', 'created_at']

@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ('user', 'full_name', 'phone', 'address_line', 'city', 'created_at')
    search_fields = ('user__full_name', 'full_name', 'phone', 'city')
    list_filter = ('created_at',)
    