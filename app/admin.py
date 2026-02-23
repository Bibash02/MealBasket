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
    list_display = ('name', 'vendor', 'category', 'price', 'created_at')
    search_fields = ('name', 'vendor__full_name', 'category__name')
    list_filter = ('created_at',)