from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class UserProfile(models.Model):
    ROLE_CHOICES = (
        ('customer', 'Customer'),
        ('vendor', 'Vendor'),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='customer')
    full_name = models.CharField(max_length=255)
    address = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.full_name} ({self.role})"
    
class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    image = models.ImageField(upload_to='category_images/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Product(models.Model):
    vendor = models.ForeignKey(UserProfile, on_delete=models.CASCADE, limit_choices_to={'role':'vendor'})
    name = models.CharField(max_length=255)
    description = models.TextField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    cook_time = models.PositiveIntegerField(default=30)
    calories = models.PositiveIntegerField(blank=True, null=True)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class CartItem(models.Model):
    customer = models.ForeignKey(UserProfile, on_delete=models.CASCADE, limit_choices_to={'role':'customer'})
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('customer', 'product')

class Order(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
        ('delivered', 'Delivered'),
    )

    customer = models.ForeignKey(UserProfile, on_delete=models.CASCADE, limit_choices_to={'role':'customer'})
    vendor = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='vendor_orders', limit_choices_to={'role':'vendor'})
    total_price = models.DecimalField(max_digits=8, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order #{self.id} by {self.customer.full_name}"
    
class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=8, decimal_places=2)  # price at order time

class ProductReview(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    customer = models.ForeignKey(UserProfile, on_delete=models.CASCADE, limit_choices_to={'role':'customer'})
    rating = models.PositiveIntegerField()  # 1 to 5
    comment = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)