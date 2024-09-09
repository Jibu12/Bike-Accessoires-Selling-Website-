from django.shortcuts import render, redirect,get_object_or_404
from django.contrib.auth import authenticate, login,logout
from .forms import CustomerRegistrationForm, CustomerLoginForm, SupplierRegistrationForm, SupplierLoginForm,CategoryForm,SubCategoryForm,ProductForm,ProductUpdateForm,AddressForm, CustomPasswordChangeForm, CheckoutForm, ProductSearchForm
from .models import *
from django.contrib.auth import get_user_model
from django.db.models import Sum
from django.db import transaction
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash
from django.db.models import F
from datetime import date
from django.utils import timezone



def base(request):
    return render(request,'base.html')


def index(request):
    
    products = Product.objects.filter(is_approved=True)
    return render(request,'index.html', {'products': products})
    
    

#---------------------------------------------------------------------------------

def admin_base(request):
    return render(request,'admin_base.html')


def admin_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('admin_home')  # Redirect to the Django admin home page
    return render(request, 'admin_login.html')


def admin_home(request):
    if not request.user.is_authenticated or not request.user.is_staff:
        return redirect('login')  # Redirect to login page if not logged in or not admin
    
    pending_products = Product.objects.filter(is_approved=False)  # Get pending products

    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        action = request.POST.get('action')
        product = get_object_or_404(Product, id=product_id)
        if action == 'approve':
            product.is_approved = True
            product.save()
        elif action == 'reject':
            product.delete()
    return render(request, 'admin_home.html', {'pending_products': pending_products})



def admin_product_approval(request):
    if not request.user.is_authenticated or not request.user.is_staff:
        return redirect('login')  # Redirect to login page if not logged in or not admin
    
    pending_products = Product.objects.filter(is_approved=False)  # Get pending products

    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        action = request.POST.get('action')
        product = get_object_or_404(Product, id=product_id)
        if action == 'approve':
            product.is_approved = True
            product.save()
        elif action == 'reject':
            product.delete()

    return render(request, 'admin_product_approval.html', {'pending_products': pending_products})



def order_history(request):
    # Fetch all orders with related order items and products
    orders = Order.objects.select_related('user', 'delivery_address').prefetch_related('orderitem_set__product', 'orderitem_set__supplier').all()
    return render(request, 'order_history.html', {'orders': orders})

def all_suppliers(request):
    suppliers = Supplier.objects.all()
    return render(request, 'all_suppliers.html', {'suppliers': suppliers})




def admin_logout(request):
    logout(request)
    return redirect('admin_login')  # Redirect to the admin login page
#--------------------------------------------------------------------------------------------------------
#--------------------------------------------------------------------------------------------------------



def supplier_base(request):
    return render(request,'supplier_base.html')


def supplier_register(request):
    if request.method == 'POST':
        form = SupplierRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('supplier_login')
    else:
        form = SupplierRegistrationForm()
    return render(request, 'supplier_register.html', {'form': form})

def supplier_login(request):
    if request.method == 'POST':
        form = SupplierLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None and user.is_supplier:
                login(request, user)
                return redirect('supplier_home')
    else:
        form = SupplierLoginForm()
    return render(request, 'supplier_login.html', {'form': form})

def supplier_home(request):
    current_supplier = request.user.supplier
    
    # Fetch orders related to products of the current supplier
    orders = OrderItem.objects.filter(supplier=current_supplier)
    
    return render(request, 'supplier_home.html', {'orders': orders})

def supplier_category_add(request):
    # Ensure supplier is logged in
    if not request.user.is_authenticated or not request.user.is_supplier:
        return redirect('supplier_login')  # Redirect to login page if not logged in
    
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('supplier_productcategory_list')  # Redirect to category list page
    else:
        form = CategoryForm()
    return render(request, 'supplier_category_add.html', {'form': form})

def supplier_subcategory_add(request):
    # Ensure supplier is logged in
    if not request.user.is_authenticated or not request.user.is_supplier:
        return redirect('supplier_login')  # Redirect to login page if not logged in
    
    if request.method == 'POST':
        form = SubCategoryForm(request.POST,request.FILES)
        if form.is_valid():
            form.save()
            return redirect('supplier_productsubcategory_list')  # Redirect to subcategory list page
    else:
        form = SubCategoryForm()
    return render(request, 'supplier_subcategory_add.html', {'form': form})


 #########################CRUD#####################################

def supplier_productadd(request):
    # Ensure supplier is logged in
    if not request.user.is_authenticated or not request.user.is_supplier:
        return redirect('supplier_login')  # Redirect to login page if not logged in
    
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            supplier = request.user.supplier  # Get the supplier object from the logged-in user
            product = form.save(commit=False)
            product.supplier = supplier
            product.save()  # Save the product after setting the supplier
            return redirect('supplier_product_list')  # Redirect to product list page
    else:
        form = ProductForm()
    return render(request, 'supplier_productadd.html', {'form': form})


def supplier_productupdate(request,product_id):
    # Ensure supplier is logged in
    if not request.user.is_authenticated or not request.user.is_supplier:
        return redirect('supplier_login')  # Redirect to login page if not logged in
    product = get_object_or_404(Product, id=product_id)
    
    if request.method == 'POST':
        form = ProductUpdateForm(request.POST, instance=product)
        if form.is_valid():
            # Update only allowed fields
            
            product.description = form.cleaned_data['description']
            product.selling_price = form.cleaned_data['selling_price']
            product.original_price = form.cleaned_data['original_price']
            product.reorder_level = form.cleaned_data['reorder_level']
            product.availability = form.cleaned_data['availability']
            # Temporary storage for additional stock quantity
            additional_quantity = form.cleaned_data['additional_quantity']
            if additional_quantity:
                product.stock_quantity += additional_quantity
            product.save()
            return redirect('supplier_product_details', product_id=product.id)
    else:
        form = ProductUpdateForm(instance=product)
    
    # Get all product details for display
    all_product_details = {
        'Product Name': product.product_name,
        'Company Name': product.company_name,
        'Bike Name': product.bike_name,
        'Product Size': product.product_size,
        'Description': product.description,
        'Selling Price': product.selling_price,
        'Original Price': product.original_price,
        'Stock Quantity': product.stock_quantity,
        'Reorder Level': product.reorder_level,
        'Availability': product.availability,
        # Add other fields as needed
    }
    
    return render(request, 'supplier_productupdate.html', {'form': form, 'product': product, 'all_product_details': all_product_details})

def supplier_productdelete(request, product_id):
    # Ensure supplier is logged in
    if not request.user.is_authenticated or not request.user.is_supplier:
        return redirect('supplier_login')  # Redirect to login page if not logged in
    product = get_object_or_404(Product, id=product_id)
    if request.method == 'POST':
        product.delete()
        return redirect('supplier_product_list')
    return render(request, 'supplier_productdelete.html', {'product': product})

            ###################################################################################################################################

def supplier_productcategory_list(request):
    # Ensure supplier is logged in
    if not request.user.is_authenticated or not request.user.is_supplier:
        return redirect('supplier_login')  # Redirect to login page if not logged in
    
    categories = Category.objects.all()
    return render(request, 'supplier_productcategory_list.html', {'categories': categories})




def supplier_productsubcategory_list(request):
    # Ensure supplier is logged in
    if not request.user.is_authenticated or not request.user.is_supplier:
        return redirect('supplier_login')  # Redirect to login page if not logged in
    
    subcategories = SubCategory.objects.all()
    return render(request, 'supplier_productsubcategory_list.html', {'subcategories': subcategories})


def supplier_product_list(request):
    # Ensure supplier is logged in
    if not request.user.is_authenticated or not request.user.is_supplier:
        return redirect('supplier_login')  # Redirect to login page if not logged in
    
    # Filter products based on the logged-in supplier
    products = Product.objects.filter(supplier=request.user.supplier)
    return render(request, 'supplier_product_list.html', {'products': products})


def supplier_product_details(request, product_id):
    # Ensure supplier is logged in
    if not request.user.is_authenticated or not request.user.is_supplier:
        return redirect('supplier_login')  # Redirect to login page if not logged in
    
    product = get_object_or_404(Product, pk=product_id)
    return render(request, 'supplier_product_details.html', {'product': product})


def supplier_change_order_status(request, order_item_id):
    order_item = get_object_or_404(OrderItem, pk=order_item_id)
    
    if request.method == 'POST':
        new_status = request.POST.get('new_status')
        order_item.item_status = new_status
        order_item.save()
        return redirect('supplier_home')

    return render(request, 'supplier_change_order_status.html', {'order_item': order_item})


def update_expected_delivery_date(request, order_item_id):
    if request.method == 'POST':
        new_delivery_date = request.POST.get('new_delivery_date')
        if new_delivery_date:
            new_delivery_date = date.fromisoformat(new_delivery_date)
            today = timezone.now().date()
            tomorrow = today + timezone.timedelta(days=1)

            if new_delivery_date <= today:
                messages.error(request, "Expected delivery date cannot be today or before today.")
            else:
                order_item = OrderItem.objects.get(pk=order_item_id)
                order_item.expected_delivery_date = new_delivery_date
                order_item.save()
                messages.success(request, "Expected delivery date updated successfully.")
        else:
            messages.error(request, "Invalid delivery date.")

    return redirect('supplier_home')  # Adjust the redirect as per your URL patterns
    
def low_stock_notifications(request):
    if not request.user.is_authenticated or not request.user.is_supplier:
        return redirect('supplier_login')  # Redirect to login page if not logged in

    supplier = request.user.supplier
    low_stock_notifications = Product.objects.filter(
        supplier=supplier,
        stock_quantity__lte=F('reorder_level')
    )

    return render(request, 'low_stock_email.html', {'low_stock_notifications': low_stock_notifications})

def supplier_logout(request):
    logout(request)
    return redirect('index') 
#---------------------------------------------------------------------------------

#---------------------------------------------------------------------------------

def customer_base(request):
    # Filter categories based on certain criteria, such as only active categories
    return render(request, 'customer_base.html')

def customer_register(request):
    if request.method == 'POST':
        form = CustomerRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('customer_login')
    else:
        form = CustomerRegistrationForm()
    return render(request, 'customer_register.html', {'form': form})

def customer_login(request):
    if request.method == 'POST':
        form = CustomerLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None and user.is_customer:
                login(request, user)
                return redirect('customer_home')
    else:
        form = CustomerLoginForm()
    return render(request, 'customer_login.html', {'form': form})


def customer_home(request):
    if request.user.is_authenticated and request.user.is_customer:
        products = Product.objects.filter(is_approved=True)
        return render(request, 'customer_home.html', {'products': products})
    else:
        return redirect('customer_login')


def customer_product_details(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    subcategory = product.subcategory
    category = subcategory.category
    context = {
        'product': product,
        'subcategory': subcategory,
        'category': category
    }
    return render(request, 'customer_product_details.html', context)



def add_to_cart(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    
    if product.selling_price is None:
        # Handle the case where selling_price is not set for the product
        return redirect('error_page')  # Redirect to an error page or handle the error as appropriate
    
    # Fetch the CustomUser instance associated with the current user
    User = get_user_model()
    user_instance = get_object_or_404(User, pk=request.user.pk)
    
    # Now fetch the associated Customer instance
    try:
        customer = Customer.objects.get(user=user_instance)
    except Customer.DoesNotExist:
        # Handle the case where Customer instance does not exist for the user
        # You can redirect the user to a registration page or handle it as appropriate
        return redirect('customer_home')
    
    # Now you can use 'customer' as the customer in the cart
    customer_cart, _ = Cart.objects.get_or_create(customer=customer)
    try:
        cart_item = CartItem.objects.get(cart=customer_cart, product=product)
        cart_item.quantity += 1
    except CartItem.DoesNotExist:
        cart_item = CartItem.objects.create(cart=customer_cart, product=product, quantity=1)

    cart_item.sub_total = cart_item.quantity * product.selling_price
    cart_item.save()

    customer_cart.total_price = CartItem.objects.filter(cart=customer_cart).aggregate(Sum('sub_total'))['sub_total__sum']
    customer_cart.save()

    return redirect('customer_cart_view')



def customer_cart_view(request):
    try:
        customer = request.user.customer  # Assuming 'customer' is the related_name for the OneToOneField in CustomUser
    except Customer.DoesNotExist:
        # Handle the case where the user is not a customer
        return render(request, 'error_page.html', {'error_message': 'You are not logged in as a customer.'})
    
    customer_cart, _ = Cart.objects.get_or_create(customer=customer)
    cart_items = CartItem.objects.filter(cart=customer_cart)
    total_price = customer_cart.total_price

    context = {'cart_items': cart_items, 'total_price': total_price}
    return render(request, 'customer_cart_view.html', context)





def increase_quantity(request, item_id):
    cart_item = get_object_or_404(CartItem, cart_item_id=item_id)
    
    if cart_item.quantity < cart_item.product.stock_quantity:  # Check if increasing would exceed available quantity
        cart_item.quantity += 1
        cart_item.subtotal_price = cart_item.quantity * cart_item.product.selling_price
        cart_item.save()

        update_cart_total(cart_item.cart)

    return redirect('customer_cart_view')



def decrease_quantity(request, item_id):
    cart_item = get_object_or_404(CartItem, cart_item_id=item_id)
    
    if cart_item.quantity > 1:
        cart_item.quantity -= 1
        cart_item.sub_total = cart_item.quantity * cart_item.product.selling_price
        cart_item.save()

        update_cart_total(cart_item.cart)

    return redirect('customer_cart_view')


def update_cart_total(cart):
    cart.total_price = CartItem.objects.filter(cart=cart).aggregate(Sum('sub_total'))['sub_total__sum']
    cart.save()


def remove_from_cart(request, cart_item_id):
    cart_item = get_object_or_404(CartItem, cart_item_id=cart_item_id)
    
    # Remove the cart item
    cart_item.delete()

    return redirect('customer_cart_view')  # Redirect to the user's cart view


def customer_checkout(request):
    # Check if the user is an instance of the Customer model
    if not request.user.is_customer:
        messages.error(request, "You need to be a customer to checkout.")
        return redirect('customer_login')  # Redirect to login page or any other appropriate page

    cart = Cart.objects.filter(customer=request.user.customer).first()
    if not cart or not cart.cartitem_set.exists():
        return redirect('customer_home')
    
    cart_items = cart.cartitem_set.all()
    total_price = cart.total_price

    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            phone = form.cleaned_data['phone']
            email = form.cleaned_data['email']
            address = form.cleaned_data['address']
            city = form.cleaned_data['city']
            state = form.cleaned_data['state']
            pincode = form.cleaned_data['pincode']

            # Create delivery address
            delivery_address = DeliveryAddress.objects.create(
                name=name,
                phone_number=phone,
                email=email,
                address=address,
                city=city,
                state=state,
                pincode=pincode
            )

            # Create order
            with transaction.atomic():
                order = Order.objects.create(
                    user=request.user.customer,
                    total_price=total_price,
                    delivery_address=delivery_address
                )

                # Create order items and deduct stock quantity
                for item in cart_items:
                    OrderItem.objects.create(
                        order=order,
                        product=item.product,
                        quantity=item.quantity,
                        unit_price=item.product.selling_price,
                        supplier=item.product.supplier,
                        item_status='Pending'
                    )

                    # Deduct stock quantity from product
                    item.product.stock_quantity -= item.quantity
                    item.product.save()

                # Clear the cart
                cart.cartitem_set.all().delete()

            return redirect('customer_order_confirmation', order_id=order.order_id)
    else:
        form = CheckoutForm()

    return render(request, 'customer_checkout.html', {'cart_items': cart_items, 'total_price': total_price, 'form': form})
# def customer_checkout(request):
#     # Check if the user is an instance of the Customer model
#     if not request.user.is_customer:
#         messages.error(request, "You need to be a customer to checkout.")
#         return redirect('customer_login')  # Redirect to login page or any other appropriate page

#     cart = Cart.objects.filter(customer=request.user.customer).first()
#     if not cart or not cart.cartitem_set.exists():
#         return redirect('customer_home')
    
#     cart_items = cart.cartitem_set.all()
#     total_price = cart.total_price

#     if request.method == 'POST':
#         name = request.POST.get('name')
#         phone = request.POST.get('phone')
#         email = request.POST.get('email')
#         address = request.POST.get('address')
#         city = request.POST.get('city')
#         state = request.POST.get('state')
#         pincode = request.POST.get('pincode')

#         # Create delivery address
#         delivery_address = DeliveryAddress.objects.create(
#             name=name,
#             phone_number=phone,
#             email=email,
#             address=address,
#             city=city,
#             state=state,
#             pincode=pincode
#         )

#         # Create order
#         with transaction.atomic():
#             order = Order.objects.create(
#                 user=request.user.customer,
#                 total_price=total_price,
#                 delivery_address=delivery_address
#             )

#             # Create order items and deduct stock quantity
#             for item in cart_items:
#                 OrderItem.objects.create(
#                     order=order,
#                     product=item.product,
#                     quantity=item.quantity,
#                     unit_price=item.product.selling_price,
#                     supplier=item.product.supplier,
#                     item_status='Pending'
#                 )

#                 # Deduct stock quantity from product
#                 item.product.stock_quantity -= item.quantity
#                 item.product.save()

#             # Clear the cart
#             cart.cartitem_set.all().delete()

#         return redirect('customer_order_confirmation', order_id=order.order_id)

#     return render(request, 'customer_checkout.html', {'cart_items': cart_items, 'total_price': total_price})




def customer_order_confirmation(request, order_id):
    order = Order.objects.get(order_id=order_id)
    return render(request, 'customer_order_confirmation.html', {'order': order})



def customer_orders(request):
    if not request.user.is_authenticated:
        return redirect('customer_login')

    # Fetch products ordered by the customer
    customer = request.user.customer  # Retrieve the customer instance associated with the user
    products = Product.objects.filter(orderitem__order__user=customer).distinct()

    return render(request, 'customer_orders.html', {'products': products})




def category_subcategory_view(request):
    categories = Category.objects.all()
    context = {'categories': categories}
    return render(request, 'category_subcategory.html', context)


from django.views.generic import ListView
from django.http import JsonResponse
class CategoryListView(ListView):
    model = Category
    template_name = 'categories.html'
    context_object_name = 'categories'


def category_list(request):
    categories = Category.objects.all()
    print("Categories:", categories)
    return render(request, 'categories.html', {'categories': categories})


def subcategory_page(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    subcategories = SubCategory.objects.filter(category=category)
    return render(request, 'subcategory_view.html', {'category': category, 'subcategories': subcategories})


def subcategory_products(request, subcategory_id):
    subcategory = get_object_or_404(SubCategory, id=subcategory_id)
    products = Product.objects.filter(subcategory=subcategory)
    context = {
        'subcategory': subcategory,
        'products': products
    }
    return render(request, 'subcategory_products.html', context)






@login_required
def customer_profile(request):
    customer = Customer.objects.get(user=request.user)
    address, created = Address.objects.get_or_create(customer=customer)
    
    if request.method == 'POST':
        address_form = AddressForm(request.POST, instance=address)
        password_form = CustomPasswordChangeForm(request.user, request.POST)
        
        if address_form.is_valid():
            address_form.save()
            messages.success(request, 'Your address has been updated.')
        elif password_form.is_valid():
            user = password_form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Your password has been changed.')
            return redirect('customer_profile')
    else:
        address_form = AddressForm(instance=address)
        password_form = CustomPasswordChangeForm(request.user)
    
    return render(request, 'customer_profile.html', {
        'address_form': address_form,
        'password_form': password_form,
    })



from django.db.models import Q


def customer_bike_product_list(request, bike_name=None):
    if bike_name:
        products = Product.objects.filter(Q(bike_name__iexact=bike_name) & Q(is_approved=True))
    else:
        products = Product.objects.filter(is_approved=True)
    bike_names = Product.objects.values_list('bike_name', flat=True).distinct()
    return render(request, 'customer_bike_product_list.html', {
        'bike_name': bike_name,
        'products': products,
        'bike_names': bike_names
    })





def customer_logout(request):
    logout(request)
    return redirect('index') 
#---------------------------------------------------------------------------------







def customer_search_products(request):
    form = ProductSearchForm(request.GET)
    products = Product.objects.all()

    if form.is_valid():
        category = form.cleaned_data.get('category')
        subcategory = form.cleaned_data.get('subcategory')
        product_name = form.cleaned_data.get('product_name')
        company_name = form.cleaned_data.get('company_name')
        bike_name = form.cleaned_data.get('bike_name')

        if category:
            products = products.filter(subcategory__category__category_name__icontains=category)

        if subcategory:
            products = products.filter(subcategory__subcategory_name__icontains=subcategory)

        if product_name:
            products = products.filter(product_name__icontains=product_name)

        if company_name:
            products = products.filter(company_name__icontains=company_name)

        if bike_name:
            products = products.filter(bike_name__icontains=bike_name)

    return render(request, 'customer_search_results.html', {'form': form, 'products': products})











