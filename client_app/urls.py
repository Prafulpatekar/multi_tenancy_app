from django.urls import include, path
from client_app.views import RolesViewSet,StoreViewSet

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    path('roles/', RolesViewSet.as_view({'get': 'list','post':'create'}), name='Vendors Roles'),
    path('roles/<int:role_id>/', RolesViewSet.as_view({'get': 'retrieve','patch':'partial_update','delete':'destroy'}), name='Roles Details'),

    path('stores/', StoreViewSet.as_view({'get': 'list','post':'create'}), name='Vendor Stores'),
    path('stores/<int:store_id>/', StoreViewSet.as_view({'get': 'retrieve','patch':'partial_update','delete':'destroy'}), name='Stores Details'),
]