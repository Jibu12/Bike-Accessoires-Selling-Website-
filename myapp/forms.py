from django import forms
from .models import CustomUser, Customer, Supplier,Category,SubCategory,Product,Address
from django.core.exceptions import ValidationError
from django.core.validators import EmailValidator, RegexValidator
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import password_validation


class CustomerRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, validators=[
        RegexValidator(
            regex=r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@])[A-Za-z\d@]{8,}$',
            message='Password must contain at least one uppercase letter, one lowercase letter, one number, and one @ symbol.'
        )
    ])
    confirm_password = forms.CharField(widget=forms.PasswordInput)
    username = forms.CharField()  # Add username field

    class Meta:
        model = Customer
        fields = ['username', 'first_name', 'last_name', 'email', 'phone_number']

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if CustomUser.objects.filter(username=username).exists():
            raise ValidationError("Username already exists.")
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if CustomUser.objects.filter(email=email).exists():
            raise ValidationError("Email already exists.")
        EmailValidator()(email)
        return email

    def clean_first_name(self):
        first_name = self.cleaned_data.get('first_name')
        if not first_name.isalpha():
            raise ValidationError("First name should contain only letters.")
        return first_name

    def clean_last_name(self):
        last_name = self.cleaned_data.get('last_name')
        if not last_name.isalpha():
            raise ValidationError("Last name should contain only letters.")
        return last_name

    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')
        if not phone_number.isdigit() or len(phone_number) != 10:
            raise ValidationError("Phone number must contain exactly 10 digits.")
        return phone_number

    def clean_confirm_password(self):
        password = self.cleaned_data.get('password')
        confirm_password = self.cleaned_data.get('confirm_password')

        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError("Passwords don't match.")
        
        return confirm_password

    def save(self, commit=True):
        user = CustomUser.objects.create_user(
            username=self.cleaned_data['username'],
            email=self.cleaned_data['email'],
            password=self.cleaned_data['password'],
            is_customer=True
        )
        customer = super().save(commit=False)
        customer.user = user
        if commit:
            customer.save()
        return customer

class CustomerLoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)

class SupplierRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, validators=[
        RegexValidator(
            regex=r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@])[A-Za-z\d@]{8,}$',
            message='Password must contain at least one uppercase letter, one lowercase letter, one number, and one @ symbol.'
        )
    ])
    confirm_password = forms.CharField(widget=forms.PasswordInput)
    username = forms.CharField()  # Add username field
    class Meta:
        model = Supplier
        fields = ['username', 'company_name', 'location', 'email', 'phone_number']

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if CustomUser.objects.filter(username=username).exists():
            raise ValidationError("Username already exists.")
        return username

    def clean_company_name(self):
        company_name = self.cleaned_data['company_name']
        if Supplier.objects.filter(company_name=company_name).exists():
            raise forms.ValidationError("This company name is already taken.")
        return company_name

    def clean_location(self):
        location = self.cleaned_data['location']
        if not location.isalpha():
            raise forms.ValidationError("Location must contain only letters.")
        return location

    def clean_email(self):
        email = self.cleaned_data['email']
        if CustomUser.objects.filter(email=email).exists():
            raise forms.ValidationError("This email is already taken.")
        return email

    def clean_phone_number(self):
        phone_number = self.cleaned_data['phone_number']
        if not phone_number.isdigit() or len(phone_number) != 10:
            raise forms.ValidationError("Phone number must contain exactly 10 digits.")
        return phone_number

    def clean_confirm_password(self):
        password = self.cleaned_data.get('password')
        confirm_password = self.cleaned_data.get('confirm_password')

        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError("Passwords don't match.")
        
        return confirm_password

    def save(self, commit=True):
        user = CustomUser.objects.create_user(
            username=self.cleaned_data['username'],
            email=self.cleaned_data['email'],
            password=self.cleaned_data['password'],
            is_supplier=True
        )
        supplier = super().save(commit=False)
        supplier.user = user
        if commit:
            supplier.save()
        return supplier
    
class SupplierLoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)



class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['category_name', 'status']

    def clean_category_name(self):
        category_name = self.cleaned_data.get('category_name')
        if Category.objects.filter(category_name=category_name).exists():
            raise forms.ValidationError("This category already exists.")
        return category_name

class SubCategoryForm(forms.ModelForm):
    class Meta:
        model = SubCategory
        fields = ['category', 'subcategory_name', 'image', 'status']

    def clean(self):
        cleaned_data = super().clean()
        category = cleaned_data.get('category')
        subcategory_name = cleaned_data.get('subcategory_name')
        if SubCategory.objects.filter(category=category, subcategory_name=subcategory_name).exists():
            raise forms.ValidationError("This subcategory already exists.")
        return cleaned_data



class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['subcategory', 'product_name', 'company_name', 'bike_name', 'product_size', 'description', 'selling_price', 'original_price', 'stock_quantity', 'reorder_level', 'availability', 'product_image1', 'product_image2', 'best_seller', 'weight', 'material_type', 'warranty_features', 'color', 'is_featured', 'feature1', 'feature2', 'feature3']  # Update fields list to include new fields

    
    def clean_selling_price(self):
        selling_price = self.cleaned_data.get('selling_price')
        if selling_price <= 0:
            raise forms.ValidationError("Selling price must be greater than zero.")
        return selling_price

    def clean_original_price(self):
        original_price = self.cleaned_data.get('original_price')
        if original_price <= 0:
            raise forms.ValidationError("Original price must be greater than zero.")
        return original_price

    def clean_stock_quantity(self):
        stock_quantity = self.cleaned_data.get('stock_quantity')
        if stock_quantity <= 0:
            raise forms.ValidationError("Stock quantity must be greater than zero.")
        return stock_quantity




class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = ['home', 'street', 'city', 'state', 'zip_code']

class CustomPasswordChangeForm(PasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['old_password'].widget.attrs.update({'class': 'form-control'})
        self.fields['new_password1'].widget.attrs.update({'class': 'form-control'})
        self.fields['new_password2'].widget.attrs.update({'class': 'form-control'})



class ProductUpdateForm(forms.ModelForm):
    additional_quantity = forms.IntegerField(label='Additional Stock Quantity', required=False)

    class Meta:
        model = Product
        fields = ['description', 'selling_price', 'original_price', 'reorder_level', 'availability']


class ProductSearchForm(forms.Form):
    category = forms.CharField(required=False)
    subcategory = forms.CharField(required=False)
    product_name = forms.CharField(required=False)
    company_name = forms.CharField(required=False)
    bike_name = forms.CharField(required=False)


class CheckoutForm(forms.Form):
    name = forms.CharField(max_length=100, required=True)
    phone = forms.CharField(max_length=20, required=True)
    email = forms.EmailField(required=False)
    address = forms.CharField(max_length=255, widget=forms.Textarea(attrs={'rows': 3}), required=True)
    city = forms.CharField(max_length=100, required=True)
    state = forms.CharField(max_length=100, required=True)
    pincode = forms.CharField(max_length=6, required=True)

    def clean_phone(self):
        phone = self.cleaned_data['phone']
        if not phone.isdigit() or len(phone) != 10:
            raise forms.ValidationError("Phone number must contain exactly 10 digits.")
        return phone

    def clean_pincode(self):
        pincode = self.cleaned_data['pincode']
        if not pincode.isdigit() or len(pincode) != 6:
            raise forms.ValidationError("Pincode must contain exactly 6 digits.")
        return pincode