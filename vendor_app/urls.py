from django.urls import include, path
from vendor_app.views import VendorViewSet

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    path('<int:vendor_id>/', VendorViewSet.as_view({'get': 'retrieve','patch':'partial_update','delete':'destroy'}), name='vendor-detail'),
    path('', VendorViewSet.as_view({'get': 'list','post':'create'}), name='Vendors List and Create'),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
]