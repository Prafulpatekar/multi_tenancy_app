from django.urls import  path
from client_app.views import (
    RolesViewSet,
    StoreViewSet,
    ProductViewSet,
    SaleViewSet,
    CustomerViewSet,
    CustomerStoresViewSet,
    CustomerProductsViewSet
)

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    path('roles/', RolesViewSet.as_view({'get': 'list','post':'create'}), name='Vendors Roles'),
    path('roles/<int:role_id>/', RolesViewSet.as_view({'get': 'retrieve','patch':'partial_update','delete':'destroy'}), name='Roles Details'),

    path('stores/', StoreViewSet.as_view({'get': 'list','post':'create'}), name='Vendor Stores'),
    path('stores/<int:store_id>/', StoreViewSet.as_view({'get': 'retrieve','patch':'partial_update','delete':'destroy'}), name='Stores Details'),

    path('stores/<int:store_id>/product/', ProductViewSet.as_view({'get': 'list','post':'create'}), name='Stores Products'),
    path('stores/<int:store_id>/product/<int:product_id>/', ProductViewSet.as_view({'get': 'retrieve','patch':'partial_update','delete':'destroy'}), name='Product Details'),

    path('sales/', SaleViewSet.as_view({'get': 'list','post':'create'}), name='Sales'),

    path('register/', CustomerViewSet.as_view({'post':'create'}), name='Register Customer'),
    path('login/', CustomerViewSet.as_view({'post':'login'}), name='Customer Login'),
    
    path('customer/stores/', CustomerStoresViewSet.as_view({'get':'get_stores'}), name='Stores'), # all stores
    path('customer/stores/<int:store_id>/', CustomerStoresViewSet.as_view({'get':'get_store'}), name='One Store'), # one store
    path('customer/stores/<int:store_id>/products', CustomerStoresViewSet.as_view({'get':'get_store_products'}), name='Store Products'), # one store all products

    path('customer/products/<int:product_id>/', CustomerProductsViewSet.as_view({'get':'get_product'}), name='Products'),# products
    path('customer/products/', CustomerProductsViewSet.as_view({'get':'get_products'}), name='One Product'),# one product
    
]