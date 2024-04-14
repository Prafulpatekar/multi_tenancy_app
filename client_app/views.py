from vendor_app.models import BaseCustomUser
from rest_framework import permissions, viewsets
from django_tenants.utils import get_tenant_model
from client_app.models import Store,Product,Sale

from client_app.serializers import (
    RolesRetrieveSerializer,
    RolesCreateSerializer,
    RolesUpdateSerializer,
    StoresCreateSerializer,
    StoresRetrieveSerializer
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



# Create your views here.
class RolesViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows client to be viewed or edited.
    """
    queryset = BaseCustomUser.objects.exclude(role=BaseCustomUser.Role.CUSTOMER)
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = RolesRetrieveSerializer
    pagination_class = CustomPagination

    def get_serializer_class(self,*args,**kwargs):
        if self.action in ['create']:
            return RolesCreateSerializer
        if self.action in ['update']:
            return RolesUpdateSerializer
        return RolesRetrieveSerializer
    
    def get_queryset(self):
        tenant_model = get_tenant_model()
        tenant = tenant_model.objects.get(domain_url=self.request.tenant.domain_url)
        return tenant.roles.all()
    
    def get_object(self):
        tenant_model = get_tenant_model()
        tenant = tenant_model.objects.get(domain_url=self.request.tenant.domain_url)
        queryset = tenant.roles.all()
        obj = queryset.filter(id=self.kwargs.get('role_id')).first()
        if obj is None:
            False
        return obj

    def create(self, request, *args, **kwargs):
        serializer_class = self.get_serializer_class()
        serializer = serializer_class(data=request.data)
        response_data = {}
        if serializer.is_valid():
            if serializer.data["role"] == BaseCustomUser.Role.ADMIN:
                user = BaseCustomUser.objects.create_user(
                    name=serializer.data["name"],
                    role=serializer.data["role"],
                    email=serializer.data["email"],
                    password=serializer.data["password"],
                    is_staff=True,
                    is_active=True,
                    is_superuser=True
                    )
                user.save()
            else:
                user = BaseCustomUser.objects.create_user(
                    name=serializer.data["name"],
                    role=serializer.data["role"],
                    email=serializer.data["email"],
                    password=serializer.data["password"],
                    is_staff=True,
                    is_active=True,
                    is_superuser=False
                    )
                user.save()
            role = BaseCustomUser.objects.get(email=serializer.data["email"])
            tenant_model = get_tenant_model()
            tenant = tenant_model.objects.get(domain_url=self.request.tenant.domain_url)
            role.client = tenant
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
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(data=serializer.data)
    

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        if not instance:
            return Response({"message":"Not found"},status=status.HTTP_404_NOT_FOUND)
        serializer = self.get_serializer(instance)
        return Response({"data":serializer.data})

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()   
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if not instance:
            return Response(status=status.HTTP_404_NOT_FOUND)
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    

class StoreViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows client to be viewed or edited.
    """
    queryset = Store.objects.filter(is_deleted=False)
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = StoresRetrieveSerializer
    pagination_class = CustomPagination

    def get_logged_in_user_id(self):
        return self.request.user.id

    def get_serializer_class(self,*args,**kwargs):
        if self.action in ['create','update']:
            return StoresCreateSerializer
        return StoresRetrieveSerializer

    def create(self, request, *args, **kwargs):
        serializer_class = self.get_serializer_class()
        serializer = serializer_class(data=request.data)
        response_data = {}
        if serializer.is_valid():
            store = Store.objects.create(
                name=serializer.data["name"],
                location=serializer.data["location"],
                contact=serializer.data["contact"],
            )
            creator = BaseCustomUser.objects.get(id=self.get_logged_in_user_id())
            store.vendor = creator.client
            store.creator = creator
            store.save()
            response_data["status"] = True
            response_data["message"] = 'Store created successfully!'
            response_data["data"] = serializer.data
            return Response(response_data, status=status.HTTP_201_CREATED)
        response_data["status"] = False
        response_data["message"] = serializer.error_messages
        response_data["data"] = serializer.errors
        return Response(response_data, status=status.HTTP_400_BAD_REQUEST)
    
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(data=serializer.data)
    

    def retrieve(self, request, *args, **kwargs):
        tenant_model = get_tenant_model()
        tenant = tenant_model.objects.get(domain_url=self.request.tenant.domain_url)
        store_id = kwargs.get("store_id")
        try:
            instance = Store.objects.get(id=store_id,vendor=tenant,creator_id=self.get_logged_in_user_id(),is_deleted=False)
        except Store.DoesNotExist:
            return Response({"message": "Store not found"}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = self.get_serializer(instance)
        return Response({"data":serializer.data})

    def partial_update(self, request, *args, **kwargs):
        tenant_model = get_tenant_model()
        tenant = tenant_model.objects.get(domain_url=self.request.tenant.domain_url)
        store_id = kwargs.get("store_id")
        try:
            instance = Store.objects.get(id=store_id,vendor=tenant,creator_id=self.get_logged_in_user_id(),is_deleted=False)
        except Store.DoesNotExist:
            return Response({"message": "Store not found"}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()   
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        tenant_model = get_tenant_model()
        tenant = tenant_model.objects.get(domain_url=self.request.tenant.domain_url)
        store_id = kwargs.get("store_id")
        try:
            instance = Store.objects.get(id=store_id,vendor=tenant,creator_id=self.get_logged_in_user_id(),is_deleted=False)
        except Store.DoesNotExist:
            return Response({"message": "Store alredy deleted"}, status=status.HTTP_404_NOT_FOUND)
        instance.is_deleted = True
        instance.save()
        return Response(status=status.HTTP_204_NO_CONTENT)