from django.urls import path
from . import views
from .views import CategoryListView

urlpatterns = [

    path('',views.index,name="index"),
    path('index',views.index,name="index"),
    path('base',views.base,name="base"),
    
    path('admin_base',views.admin_base,name="admin_base"),
    path('admin_login', views.admin_login, name='admin_login'),
    path('admin_home', views.admin_home, name='admin_home'),
    path('admin_product_approval', views.admin_product_approval, name='admin_product_approval'),
    path('order-history/', views.order_history, name='order_history'),
    path('all_suppliers/', views.all_suppliers, name='all_suppliers'),
    path('admin_logout/', views.admin_logout, name='admin_logout'),





    path('supplier_base', views.supplier_base, name='supplier_base'),
    path('supplier_register', views.supplier_register, name='supplier_register'),
    path('supplier_login', views.supplier_login, name='supplier_login'),
    path('supplier_home', views.supplier_home, name='supplier_home'),
    path('supplier_category_add', views.supplier_category_add, name="supplier_category_add"),
    path('supplier_subcategory_add', views.supplier_subcategory_add, name="supplier_subcategory_add"),
    path('supplier_productadd', views.supplier_productadd, name="supplier_productadd"),
    path('supplier_productupdate/<int:product_id>/', views.supplier_productupdate, name='supplier_productupdate'),
    path('supplier_productdelete/<int:product_id>/', views.supplier_productdelete, name='supplier_productdelete'),



    path('supplier_productcategory_list', views.supplier_productcategory_list, name="supplier_productcategory_list"),
    path('supplier_productsubcategory_list', views.supplier_productsubcategory_list, name="supplier_productsubcategory_list"),
    path('supplier_product_list', views.supplier_product_list, name="supplier_product_list"),
    path('supplier_product_details/<int:product_id>/', views.supplier_product_details, name='supplier_product_details'),
    path('supplier_update_order_item_status/<int:order_item_id>/',views.supplier_change_order_status, name='update_order_item_status'),
    path('supplier_orders_update_delivery_date/<int:order_item_id>/', views.update_expected_delivery_date, name='update_expected_delivery_date'),
    path('low-stock-notifications/', views.low_stock_notifications, name='low_stock_notifications'),

    path('supplier_logout', views.supplier_logout, name="supplier_logout"),


    path('customer_register', views.customer_register, name='customer_register'),
    path('customer_login', views.customer_login, name='customer_login'),
    path('customer_home', views.customer_home, name='customer_home'),
    path('customer_product_details/<int:product_id>/', views.customer_product_details, name='customer_product_details'),
    path('customer_cart_view', views.customer_cart_view, name='customer_cart_view'),
    path('add_to_cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('increase-quantity/<int:item_id>/', views.increase_quantity, name='increase_quantity'),
    path('decrease-quantity/<int:item_id>/', views.decrease_quantity, name='decrease_quantity'),
    path('remove_from_cart/<int:cart_item_id>/', views.remove_from_cart, name='remove_from_cart'),



    path('customer_checkout/', views.customer_checkout, name='customer_checkout'),
    path('customer_order_confirmation/<int:order_id>/', views.customer_order_confirmation, name='customer_order_confirmation'),
    path('customer_orders/', views.customer_orders, name='customer_orders'),


    path('customer_logout', views.customer_logout, name="customer_logout"),




    path('categories/', views.category_list, name='category_list'),
    path('categories/', CategoryListView.as_view(), name='category_list'),
    path('subcategory/<int:category_id>/', views.subcategory_page, name='subcategory_page'),
    path('subcategory/products/<int:subcategory_id>/', views.subcategory_products, name='subcategory_products'), 
    path('customer_profile/', views.customer_profile, name='customer_profile'),

    path('bike/', views.customer_bike_product_list, name='bike_product_list_all'),  # For showing all products
    path('bike/<str:bike_name>/', views.customer_bike_product_list, name='bike_product_list'),  # For filtering by bike name



   
    path('customer_search/', views.customer_search_products, name='customer_search_products'),
]
