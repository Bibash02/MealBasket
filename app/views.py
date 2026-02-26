from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib import messages
from .models import *
from django.contrib.auth import authenticate, login, logout
from django.urls import reverse
from .utils import generate_signature
from django.conf import settings
import uuid
import hashlib  

# Create your views here.
def home(request):
    return render(request, 'home.html')

def auth(request):
    return render(request, 'auth.html')

def test(request):
    return render(request, 'test.html')

def signup_view(request):
    if request.method == "POST":
        full_name = request.POST.get("full_name")
        email = request.POST.get("email")
        password = request.POST.get("password")
        role = request.POST.get("role")

        if User.objects.filter(username=email).exists():
            messages.error(request, "Email already registered")
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
        elif role == "customer":
            return redirect("customer_dashboard")
        else:
            return redirect("signin")

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
            elif user.profile.role == "customer":
                return redirect("customer_dashboard")
            else:
                return redirect("signin")
        else:
            messages.error(request, "Invalid email or password")

    return render(request, "signin.html")

def logout_view(request):
    logout(request)
    return redirect('home')
    
def customer_dashboard(request):
    profile = request.user.profile

    # Ensure role is customer
    if profile.role != "customer":
        return redirect("signin")

    # All products available for customer
    products = Product.objects.all().order_by('-id')

    # Orders that belong to this customer
    # Assuming Order.customer points to UserProfile
    orders = Order.objects.filter(user=request.user).order_by('-created_at')

    categories = Category.objects.all()
    cart_count = CartItem.objects.filter(customer = profile).count()

    context = {
        'profile': profile,
        'products': products,
        'orders': orders,
        'categories': categories,
        'cart_count': cart_count,
    }

    return render(request, 'customer_dashboard.html', context)

def update_customer_profile(request):
    profile = get_object_or_404(UserProfile, user=request.user)

    if request.method == "POST":
        profile.user.first_name = request.POST.get('full_name')
        profile.address = request.POST.get('address')
        profile.user.save()
        profile.save()
        messages.success(request, 'Profile updated successfully!')
        return redirect('customer_dashboard')
    return render(request, 'update_customer_profile.html', {'profile': profile})

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
        messages.success(request, f"Added another {product.name} to your cart!")
    else:
        messages.success(request, f"{product.name} added to your cart!")

    return redirect(request.META.get('HTTP_REFERER', 'customer_dashboard'))

def view_cart(request):
    profile = get_object_or_404(UserProfile, user=request.user, role='customer')
    cart_items = CartItem.objects.filter(customer=profile)
    total = sum(item.quantity * float(item.product.price) for item in cart_items)
    return render(request, 'cart.html', {
        'cart_items': cart_items, 
        'total': total
        })

def remove_cart_item(request, item_id):
    item = get_object_or_404(CartItem, id=item_id, customer__user=request.user)
    item.delete()
    return redirect('view_cart')

def update_cart_item(request, item_id):
    action = request.GET.get('action')
    item = get_object_or_404(CartItem, id=item_id, customer__user=request.user)
    
    if action == 'increase':
        item.quantity += 1
        item.save()
    elif action == 'decrease':
        if item.quantity > 1:
            item.quantity -= 1
            item.save()
        else:
            item.delete()
    
    return redirect('view_cart')

def checkout(request):
    profile = get_object_or_404(UserProfile, user=request.user, role='customer')
    cart_items = CartItem.objects.filter(customer=profile)
    if not cart_items.exists():
        return redirect('customer_dashboard')

    total = sum(item.quantity * item.product.price for item in cart_items)
    total_amount = "{:.2f}".format(total)  # Important: 2 decimal places

    if request.method == 'POST':
        full_name = request.POST.get('full_name', request.user.get_full_name() or request.user.username)
        email = request.POST.get('email', request.user.email)
        phone = request.POST.get('phone', '')
        address_text = request.POST.get('address', '')
        city = request.POST.get('city', '')
        payment_type = request.POST.get('payment_type', 'cod')

        address = Address.objects.create(
            user=request.user,
            full_name=full_name,
            phone=phone,
            address_line=address_text,
            city=city
        )

        order = Order.objects.create(
            user=request.user,
            full_name=full_name,
            email=email,
            phone=phone,
            address=address,
            city=city,
            country="Nepal",
            amount=total,
            payment_type=payment_type,
            transaction_uuid=str(uuid.uuid4()),
            status="Pending"
        )

        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price=item.product.price
            )

        cart_items.delete()

        if payment_type == 'cod':
            order.status = 'Confirmed'
            order.save()
            return render(request, 'payment_success.html', {'order': order})

        # ======================
        # eSewa v2 Payment
        # ======================
        pid = order.transaction_uuid
        amt = total_amount
        scd = settings.ESEWA_PRODUCT_CODE  # merchant code
        secret_key = settings.ESEWA_SECRET_KEY  # merchant secret key

        # Correct signature: SHA256 of pid + amt + scd + secret_key
        signature_string = f"{pid}{amt}{scd}{secret_key}"
        signature = hashlib.sha256(signature_string.encode()).hexdigest()

        context = {
            "amt": amt,
            "pid": pid,
            "scd": scd,
            "su": request.build_absolute_uri('/payment/success/'),
            "fu": request.build_absolute_uri('/payment/failed/'),
            "signature": signature,
            "order": order
        }

        return render(request, 'esewa_payment.html', context)

    return render(request, 'checkout.html', {'cart_items': cart_items, 'total': total})

def payment_success(request):
    # Get eSewa query parameters
    pid = request.GET.get('pid')
    refId = request.GET.get('refId')

    order = get_object_or_404(Order, id=pid, customer__user=request.user)
    order.status = 'paid'
    order.esewa_tid = refId
    order.save()
    messages.success(request, 'Payment successful! Your order has been placed.')
    return redirect('customer_dashboard')

def payment_fail(request):
    pid = request.GET.get('pid')
    order = get_object_or_404(Order, id=pid, customer__user=request.user)
    order.status = 'failed'
    order.save()
    messages.error(request, 'Payment failed or cancelled. Please try again.')
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
        stock = request.POST.get('stock')
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
            stock=stock,
            cook_time=cook_time,
            calories=calories,
            image=image
        )
        return redirect('vendor_dashboard')

    return render(request, 'add_product.html', {'categories': categories})

# def edit_product(request, pk):
#     vendor_profile = get_object_or_404(UserProfile, user=request.user)
#     product = get_object_or_404(Product, pk=pk, vendor=vendor_profile)
#     categories = Category.objects.filter(is_active=True)

#     if request.method == 'POST':
#         product.name = request.POST.get('name')
#         product.description = request.POST.get('description')
#         category_id = request.POST.get('category')
#         product.category = get_object_or_404(Category, id=category_id)
#         product.price = request.POST.get('price')
#         product.stock = request.POST.get('stock')
#         product.cook_time = request.POST.get('cook_time')
#         product.calories = request.POST.get('calories') or None
#         if request.FILES.get('image'):
#             product.image = request.FILES.get('image')
#         product.save()
#         return redirect('vendor_dashboard')

#     return render(request, 'vendor_edit_product.html', {'product': product, 'categories': categories})

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
        product.stock = request.POST['stock']
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