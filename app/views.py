from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib import messages
from .models import *
from django.contrib.auth import authenticate, login, logout
from django.http import JsonResponse
from django.db.models import Sum
from django.views.decorators.csrf import csrf_exempt

# Create your views here.
def home(request):
    return render(request, 'home.html')

def auth(request):
    return render(request, 'auth.html')

def test(request):
    return render(request, 'test.html')

def signin(request):
    return render(request, 'signin.html')

def signup(request):
    return render(request, 'signup.html')


def signup_view(request):
    if request.method == "POST":
        full_name = request.POST.get("full_name")
        email = request.POST.get("email")
        password = request.POST.get("password")
        role = request.POST.get("role")

        if User.objects.filter(username=email).exists():
            messages.error(request, "Email already r    egistered")
            return redirect("signup")

        # Create user
        user = User.objects.create_user(
            username=email,
            email=email,
            password=password
        )

        user.first_name = full_name
        user.save()

        # Create UserProfile
        UserProfile.objects.create(
            user=user,
            role=role
        )

        login(request, user)

        if role == "vendor":
            return redirect("vendor_dashboard")
        else:
            return redirect("customer_dashboard")

    return render(request, "signup.html")
    
def signin_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)

            # Role-based redirect
            if user.profile.role == "vendor":
                return redirect("vendor_dashboard")
            else:
                return redirect("customer_dashboard")
        else:
            messages.error(request, "Invalid email or password")

    return render(request, "signin.html")

def logout_view(request):
    logout(request)
    return redirect('home')
    
def customer_dashboard(request):
    # Get the UserProfile for the logged-in user
    profile = get_object_or_404(UserProfile, user=request.user)
    products = Product.objects.all().order_by('-id')
    orders = Order.objects.filter(customer=profile).order_by('-created_at')
    categories = Category.objects.all()

    context = {
        'profile': profile,
        'products': products,
        'orders': orders,
        'categories': categories
    }

    return render(request, 'customer_dashboard.html', context)

def update_customer_profile(request):
    profile = get_object_or_404(UserProfile, user=request.user)

    if request.method == "POST":
        profile.user.first_name = request.POST.get('full_name')
        profile.address = request.POST.get('address')
        profile.user.save()
        profile.save()

    return redirect('customer_dashboard')

def add_to_cart(request, product_id):
    profile = get_object_or_404(UserProfile, user=request.user, role='customer')
    product = get_object_or_404(Product, id=product_id)

    cart_item, created = CartItem.objects.get_or_create(
        customer=profile,
        product=product
    )

    if not created:
        cart_item.quantity += 1
        cart_item.save()

    return redirect('customer_dashboard')

def vender_dashboard(request):
    vendor_profile = get_object_or_404(UserProfile, user=request.user)
    categories = Category.objects.all()
    products = Product.objects.filter(vendor=vendor_profile).order_by('-created_at')

    context = {
        'vendor_profile': vendor_profile,
        'categories': categories,
        'products': products,
    }
    return render(request, 'vender_dashboard.html', context)

def update_vendor_profile(request):
    vendor_profile = get_object_or_404(UserProfile, user=request.user)

    if request.method == 'POST':
        vendor_profile.full_name = request.POST.get('full_name')
        vendor_profile.address = request.POST.get('address')
        vendor_profile.save()
        messages.success(request, 'Profile updated successfully!')
        return redirect('vendor_dashboard')

    context = {'vendor_profile': vendor_profile}
    return render(request, 'update_vendor_profile.html', context)

def add_product(request):
    vendor_profile = get_object_or_404(UserProfile, user=request.user)
    categories = Category.objects.filter(is_active=True)

    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        category_id = request.POST.get('category')
        price = request.POST.get('price')
        cook_time = request.POST.get('cook_time')
        calories = request.POST.get('calories') or None
        image = request.FILES.get('image')

        category = get_object_or_404(Category, id=category_id)

        Product.objects.create(
            vendor=vendor_profile,
            name=name,
            description=description,
            category=category,
            price=price,
            cook_time=cook_time,
            calories=calories,
            image=image
        )
        return redirect('vendor_dashboard')

    return render(request, 'add_product.html', {'categories': categories})

def edit_product(request, pk):
    vendor_profile = get_object_or_404(UserProfile, user=request.user)
    product = get_object_or_404(Product, pk=pk, vendor=vendor_profile)
    categories = Category.objects.filter(is_active=True)

    if request.method == 'POST':
        product.name = request.POST.get('name')
        product.description = request.POST.get('description')
        category_id = request.POST.get('category')
        product.category = get_object_or_404(Category, id=category_id)
        product.price = request.POST.get('price')
        product.cook_time = request.POST.get('cook_time')
        product.calories = request.POST.get('calories') or None
        if request.FILES.get('image'):
            product.image = request.FILES.get('image')
        product.save()
        return redirect('vendor_dashboard')

    return render(request, 'vendor_edit_product.html', {'product': product, 'categories': categories})

def save_product(request):
    if request.method == "POST":
        product_id = request.POST.get('product_id')
        name = request.POST['name']
        description = request.POST['description']
        category_id = request.POST['category']
        price = request.POST['price']
        cook_time = request.POST.get('cook_time')  # optional
        calories = request.POST.get('calories')    # optional
        image = request.FILES.get('image')

        category = get_object_or_404(Category, id=category_id)
        vendor_profile = get_object_or_404(UserProfile, user=request.user)

        if product_id:  # Edit existing
            product = get_object_or_404(Product, id=product_id, vendor=vendor_profile)
        else:  # Add new
            product = Product(vendor=vendor_profile)

        product.name = name
        product.description = description
        product.category = category
        product.price = price
        product.cook_time = cook_time or 0
        product.calories = calories or None
        if image:
            product.image = image

        product.save()

        return redirect('vendor_dashboard')

    return redirect('vendor_dashboard')

def edit_product(request, product_id):
    vendor_profile = get_object_or_404(UserProfile, user=request.user)
    product = get_object_or_404(Product, id=product_id, vendor=vendor_profile)
    categories = Category.objects.all()

    if request.method == "POST":
        product.name = request.POST['name']
        product.description = request.POST['description']
        product.category = get_object_or_404(Category, id=request.POST['category'])
        product.price = request.POST['price']
        product.cook_time = request.POST.get('cook_time') or 0
        product.calories = request.POST.get('calories') or None
        image = request.FILES.get('image')
        if image:
            product.image = image
        product.save()
        return redirect('vendor_dashboard')

    context = {
        'product': product,
        'categories': categories,
    }
    return render(request, 'vendor_edit_product.html', context)

def delete_product(request, product_id):
    vendor_profile = get_object_or_404(UserProfile, user=request.user)
    product = get_object_or_404(Product, id=product_id, vendor=vendor_profile)
    product.delete()
    return redirect('vendor_dashboard')

def my_products(request):
    vendor_profile = get_object_or_404(UserProfile, user=request.user)
    products = Product.objects.filter(vendor=vendor_profile).order_by('-created_at')

    context = {
        "products": products
    }
    return render(request, "vendor_product_list.html", context)