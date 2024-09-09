from .models import Category,SubCategory,Product

def categories(request):
    categories = Category.objects.all()
    return {'categories': categories}

def available_bike_names(request):
    # Fetch all distinct bike names
    bike_names = Product.objects.values_list('bike_name', flat=True).distinct()
    return {'available_bike_names': bike_names}