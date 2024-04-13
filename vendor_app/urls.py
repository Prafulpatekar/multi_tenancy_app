from django.urls import include, path
from vendor_app.views import VendorViewSet,RolesViewSet

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    path('vendors/<int:vendor_id>/', VendorViewSet.as_view({'get': 'retrieve','patch':'partial_update','delete':'destroy'}), name='vendor-detail'),
    path('vendors/', VendorViewSet.as_view({'get': 'list','post':'create'}), name='vendors'),
    path('vendors/<int:vendor_id>/roles/', RolesViewSet.as_view({'get': 'list','post':'create'}), name='Vendors Roles'),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
]