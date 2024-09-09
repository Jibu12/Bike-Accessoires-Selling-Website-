from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _
from decimal import Decimal
from django.core.exceptions import ValidationError

from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags


class CustomUser(AbstractUser):
    is_customer = models.BooleanField(default=False)
    is_supplier = models.BooleanField(default=False)

class Customer(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, primary_key=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField()
    phone_number = models.CharField(max_length=20, validators=[RegexValidator(regex=r'^\+?1?\d{9,15}$', message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.")])
    # Add other fields specific to customers, like shipping address, etc.

    def __str__(self):
        return self.user.username

class Supplier(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, primary_key=True)
    company_name = models.CharField(max_length=200)
    location = models.CharField(max_length=200)
    email = models.EmailField()
    phone_number = models.CharField(max_length=15, validators=[RegexValidator(regex=r'^\+?1?\d{9,15}$', message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.")])
    registration_date = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.company_name

class Address(models.Model):
    id = models.AutoField(primary_key=True)
    home = models.CharField(max_length=55, blank=True)
    street = models.CharField(max_length=255)
    city = models.CharField(max_length=50)
    state = models.CharField(max_length=50)
    zip_code = models.CharField(max_length=10)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.street}, {self.city}, {self.state} {self.zip_code}"


class Category(models.Model):
    id = models.AutoField(primary_key=True)
    category_name = models.CharField(max_length=100)
    status = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.category_name
    

class SubCategory(models.Model):
    id = models.AutoField(primary_key=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    subcategory_name = models.CharField(max_length=100)
    image = models.ImageField(upload_to='subcategory_images/')
    status = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.subcategory_name
    
class Product(models.Model):
    id = models.AutoField(primary_key=True)
    subcategory = models.ForeignKey(SubCategory, on_delete=models.CASCADE)
    product_name = models.CharField(max_length=255)
    company_name = models.CharField(max_length=255, blank=True)
    bike_name = models.CharField(max_length=255 , blank=True)
    product_size = models.CharField(max_length=10, blank=True)  
    description = models.TextField()
    selling_price = models.DecimalField(max_digits=10, decimal_places=2)
    original_price = models.DecimalField(max_digits=10, decimal_places=2)
    stock_quantity = models.PositiveIntegerField()
    reorder_level = models.PositiveIntegerField()
    availability = models.BooleanField(default=True)
    product_image1 = models.ImageField(upload_to='product_images/')
    product_image2 = models.ImageField(upload_to='product_images/')
    best_seller = models.BooleanField(default=False)
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE) # Assuming you have a Supplier model
    is_approved = models.BooleanField(default=False)  # New field for approval status


    #newfields
    weight = models.FloatField(blank=True, null=True)
    material_type = models.CharField(max_length=100, blank=True)
    warranty_features = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    color = models.CharField(max_length=50, blank=True)
    is_featured = models.BooleanField(default=False)

    feature1 = models.CharField(max_length=500, blank=True)
    feature2 = models.CharField(max_length=500, blank=True)
    feature3 = models.CharField(max_length=500, blank=True)


    def check_stock_and_notify_supplier(self):
        if self.stock_quantity <= self.reorder_level:
            supplier_email = self.supplier.user.email
            subject = f"Low Stock Alert for {self.product_name}"
            message = render_to_string('low_stock_email.html', {'product': self})
            plain_message = strip_tags(message)
            send_mail(subject, plain_message, 'adranefox12@gmail.com', [supplier_email], html_message=message)


    def __str__(self):
        return self.product_name
    
    

class Cart(models.Model):
    cart_id = models.AutoField(primary_key=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))

    def __str__(self):
        return f"Cart for {self.cart_id}"


class CartItem(models.Model):
    cart_item_id = models.AutoField(primary_key=True)
    cart = models.ForeignKey('Cart', on_delete=models.CASCADE)
    product = models.ForeignKey('Product', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    sub_total = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"CartItem {self.cart_item_id} in Cart {self.cart.cart_id}"
    
    def clean(self):
        if self.quantity < 0:
            raise ValidationError("Quantity cannot be negative.")

    def save(self, *args, **kwargs):
        if self.product.selling_price is None:
            # Handle the case where selling_price is not set for the product
            raise ValueError("Selling price is not set for the product.")
        
        self.sub_total = self.product.selling_price * self.quantity
        super().save(*args, **kwargs)



class DeliveryAddress(models.Model):
    delivery_address_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=20)
    email = models.EmailField(max_length=100, blank=True, null=True)
    address = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    pincode = models.CharField(max_length=20)

    def __str__(self):
        return f"{self.name}, {self.address}, {self.city}, {self.state}, {self.pincode}"
    


class Order(models.Model):
    order_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(Customer, on_delete=models.CASCADE)
    order_date = models.DateTimeField(auto_now_add=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    delivery_address = models.ForeignKey(DeliveryAddress, on_delete=models.SET_NULL, null=True)


    def calculate_commission(self):
        commission_rate = AdminCommission.objects.first().commission_rate
        return (self.total_price * commission_rate) / 100

    def __str__(self):
        return f"Order ID: {self.order_id}, Total Price: {self.total_price}"



class OrderItem(models.Model):
    order_item_id = models.AutoField(primary_key=True)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Shipped', 'Shipped'),
        ('Delivered', 'Delivered'),
    ]
    # Add a field to track the status of each item in the order
    item_status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='Pending')
    expected_delivery_date = models.DateField(null=True, blank=True)
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE)  # Add supplier field

    def __str__(self):
        return f"Order Item ID: {self.order_item_id}, Product: {self.product.product_name}, Quantity: {self.quantity}, Unit Price: {self.unit_price}, Status: {self.item_status}"



class AdminCommission(models.Model):
    commission_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)
    total_commission_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)