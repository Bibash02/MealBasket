from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib import messages
from .models import *
from django.contrib.auth import authenticate, login, logout
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

# Create your views here.
def home(request):
    return render(request, 'home.html')

def auth(request):
    return render(request, 'auth.html')

def test(request):
    return render(request, 'test.html')



def signup_post(request):
    if request.method == 'POST':
        full_name = request.POST.get('signup_name')
        email = request.POST.get('signup_email')
        password = request.POST.get('signup_password')
        role = request.POST.get('signup_role')

        if User.objects.filter(username=email).exists():
            messages.error(request, "Email already registered!")
            return redirect('home')

        # Create User
        user = User.objects.create_user(username=email, email=email, password=password)

        # Create Profile
        UserProfile.objects.create(user=user, full_name=full_name, role=role)

        messages.success(request, "Account created successfully! You can now sign in.")
        return redirect('signin')
    else:
        return redirect('home')
    
def signin_post(request):
    if request.method == "POST":
        email = request.POST.get('signin_email')
        password = request.POST.get('signin_password')

        user = authenticate(request, username=email, password=password)

        if user is not None:
            login(request, user)

            # Use the correct related name
            profile = getattr(user, 'profile', None)
            if profile:
                if profile.role == 'vendor':  # lowercase
                    return redirect('vendor_dashboard')
                else:
                    return redirect('customer_dashboard')
            else:
                messages.error(request, "User profile not found!")
                return redirect('home')
        else:
            messages.error(request, "Invalid email or password")
            return redirect('signin')
    else:
        return redirect('home')

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
    if request.method == "POST":
        product.delete()
    return redirect('vender_dashboard')

def save_vendor_profile(request):
    if request.method == "POST":
        profile = request.user
        profile.business_name = request.POST.get('business_name')
        profile.phone = request.POST.get('phone')
        profile.address = request.POST.get('address')
        profile.save()

        request.user.email = request.POST.get('email')
        request.user.save()

        return JsonResponse({'status': 'success', 'message': 'Profile updated successfully'})
    return JsonResponse({'status': 'error', 'message': 'Invalid request'})