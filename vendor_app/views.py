from vendor_app.models import Client,Domain,BaseCustomUser
from rest_framework import permissions, viewsets
from django.shortcuts import get_object_or_404

from vendor_app.serializers import (
    VendorCreateSerializer,
    VendorRetrieveSerializer,
    RolesRetrieveSerializer,
    RolesCreateSerializer
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
    queryset = Client.objects.all().order_by('-created_datetime')
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
            tenant = Client.objects.filter(name=request.data['name']).first()
            domain = Domain.objects.create(tenant=tenant,domain=f"{tenant.schema_name}.localhost")
            domain.save()
            response_data["status"] = True
            response_data["message"] = 'Vendors created successfully!'
            response_data["data"] = serializer.data
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
        
        if instance.name.lower() == "public":
            return Response({"message":"Not allowed"},status=status.HTTP_405_METHOD_NOT_ALLOWED)
        partial_data = request.data
        name = partial_data.get('name')

        if name:
            instance.name = name
            instance.schema_name = name.lower().replace(" ", "")
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
        
        if instance.name.lower() == "public":
            return Response({"message":"Not allowed"},status=status.HTTP_405_METHOD_NOT_ALLOWED)
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class RolesViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows client to be viewed or edited.
    """
    queryset = BaseCustomUser.objects.exclude(role=BaseCustomUser.Role.CUSTOMER)
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = RolesRetrieveSerializer
    pagination_class = CustomPagination
    lookup_field = 'vendor_id'

    def get_serializer_class(self,*args,**kwargs):
        if self.action in ['create','update']:
            return RolesCreateSerializer
        return RolesRetrieveSerializer

    def create(self, request, *args, **kwargs):
        vendor_id = kwargs.get(self.lookup_field)  # Use the custom lookup field
        try:
            client = Client.objects.get(pk=vendor_id)
        except Client.DoesNotExist:
            return Response({"message": "Role not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer_class = self.get_serializer_class()
        serializer = serializer_class(data=request.data)
        response_data = {}
        if serializer.is_valid():
            serializer.save()
            role = BaseCustomUser.objects.get(email=serializer.data["email"])
            role.client = client
            role.save()
            response_data["status"] = True
            response_data["message"] = 'Role created successfully!'
            response_data["data"] = serializer.data
            return Response(response_data, status=status.HTTP_201_CREATED)
        response_data["status"] = False
        response_data["message"] = serializer.error_messages
        response_data["data"] = serializer.errors
        return Response(response_data, status=status.HTTP_400_BAD_REQUEST)
    
    def list(self, request, *args, **kwargs):
        vendor_id = kwargs.get(self.lookup_field)  # Use the custom lookup field
        try:
            instance = Client.objects.get(pk=vendor_id)
        except Client.DoesNotExist:
            return Response({"message": "Role not found"}, status=status.HTTP_404_NOT_FOUND)
        instance = get_object_or_404(Client,pk=vendor_id)
        queryset = instance.roles.all()
        page = self.paginate_queryset(queryset)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(data=serializer.data)

    # def retrieve(self, request, *args, **kwargs):
    #     vendor_id = kwargs.get(self.lookup_field)  # Use the custom lookup field
    #     try:
    #         instance = Client.objects.get(pk=vendor_id)
    #     except Client.DoesNotExist:
    #         return Response({"message": "Vendor not found"}, status=status.HTTP_404_NOT_FOUND)
    #     serializer = self.get_serializer(instance)
    #     response_data = {
    #         "status": True,
    #         "message": "Vendor details fetched successfully",
    #         "data": serializer.data
    #     }
    #     return Response(response_data, status=status.HTTP_200_OK)
    
    # def partial_update(self, request, *args, **kwargs):
    #     vendor_id = kwargs.get(self.lookup_field)
    #     try:
    #         instance = Client.objects.get(pk=vendor_id)
    #     except Client.DoesNotExist:
    #         return Response({"message": "Vendor not found"}, status=status.HTTP_404_NOT_FOUND)
        
    #     if instance.name.lower() == "public":
    #         return Response({"message":"Not allowed"},status=status.HTTP_405_METHOD_NOT_ALLOWED)
    #     partial_data = request.data
    #     name = partial_data.get('name')

    #     if name:
    #         instance.name = name
    #         instance.schema_name = name.lower().replace(" ", "")
    #         instance.save()
    #         serializer = self.get_serializer(instance)
    #         return Response({"status":True,"message":"Vendor updated successfully","data":serializer.data}, status=status.HTTP_200_OK)
    #     else:
    #         return Response({'error': 'Name field is required'}, status=status.HTTP_400_BAD_REQUEST)

    # def destroy(self, request, *args, **kwargs):
    #     vendor_id = kwargs.get(self.lookup_field)
    #     try:
    #         instance = Client.objects.get(pk=vendor_id)
    #     except Client.DoesNotExist:
    #         return Response({"message": "Vendor not found"}, status=status.HTTP_404_NOT_FOUND)
        
    #     if instance.name.lower() == "public":
    #         return Response({"message":"Not allowed"},status=status.HTTP_405_METHOD_NOT_ALLOWED)
    #     instance.delete()
    #     return Response(status=status.HTTP_204_NO_CONTENT)
