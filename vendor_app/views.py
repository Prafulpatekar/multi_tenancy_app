from vendor_app.models import Client,Domain
from rest_framework import permissions, viewsets
from django.shortcuts import get_object_or_404

from vendor_app.serializers import (
    VendorCreateSerializer,
    VendorRetrieveSerializer
)
from rest_framework.response import Response
from rest_framework import status

from rest_framework.pagination import PageNumberPagination

class CustomPagination(PageNumberPagination):
    def get_paginated_response(self, data, message=None, *args, **kwargs):
        return Response({
            'status': True,
            'message': message or "Data fetch successfully",
            'count': self.page.paginator.count,
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'data': data
        }, status=status.HTTP_200_OK)


class VendorViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows client to be viewed or edited.
    """
    queryset = Client.objects.all().order_by('-created_on')
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = VendorRetrieveSerializer
    pagination_class = CustomPagination
    lookup_field = 'vendor_id'

    def get_serializer_class(self,*args,**kwargs):
        if self.action in ['create','update']:
            return VendorCreateSerializer
        return VendorRetrieveSerializer

    def create(self, request, *args, **kwargs):
        serializer_class = self.get_serializer_class()
        serializer = serializer_class(data=request.data)
        response_data = {}
        if serializer.is_valid():
            serializer.save()
            tenant = Client.objects.filter(vendor_name=request.data['vendor_name']).first()
            tenant.domain_url = f"{tenant.schema_name}.localhost"
            tenant.save()
            domain = Domain.objects.create(tenant=tenant,domain=tenant.domain_url)
            domain.save()
            response_data["status"] = True
            response_data["message"] = 'Vendors created successfully!'
            response_data["data"] = serializer.data
            response_data["data"]["uuid"] = tenant.vendor_uuid
            return Response(response_data, status=status.HTTP_201_CREATED)
        response_data["status"] = False
        response_data["message"] = serializer.error_messages
        response_data["data"] = serializer.errors
        return Response(response_data, status=status.HTTP_400_BAD_REQUEST)
    
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(data=serializer.data)

    def retrieve(self, request, *args, **kwargs):
        vendor_id = kwargs.get(self.lookup_field)  # Use the custom lookup field
        try:
            instance = Client.objects.get(pk=vendor_id)
        except Client.DoesNotExist:
            return Response({"message": "Vendor not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.get_serializer(instance)
        response_data = {
            "status": True,
            "message": "Vendor details fetched successfully",
            "data": serializer.data
        }
        return Response(response_data, status=status.HTTP_200_OK)
    
    def partial_update(self, request, *args, **kwargs):
        vendor_id = kwargs.get(self.lookup_field)
        try:
            instance = Client.objects.get(pk=vendor_id)
        except Client.DoesNotExist:
            return Response({"message": "Vendor not found"}, status=status.HTTP_404_NOT_FOUND)
        
        if instance.vendor_name.lower() == "public":
            return Response({"message":"Not allowed"},status=status.HTTP_405_METHOD_NOT_ALLOWED)
        partial_data = request.data
        vendor_name = partial_data.get('vendor_name')
        description = partial_data.get('description')

        if vendor_name:
            instance.vendor_name = vendor_name
            instance.description = description
            instance.save()
            serializer = self.get_serializer(instance)
            return Response({"status":True,"message":"Vendor updated successfully","data":serializer.data}, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Name field is required'}, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        vendor_id = kwargs.get(self.lookup_field)
        try:
            instance = Client.objects.get(pk=vendor_id)
        except Client.DoesNotExist:
            return Response({"message": "Vendor not found"}, status=status.HTTP_404_NOT_FOUND)
        
        if instance.vendor_name.lower() == "public":
            return Response({"message":"Not allowed"},status=status.HTTP_405_METHOD_NOT_ALLOWED)
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
