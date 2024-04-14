from vendor_app.models import BaseCustomUser
from rest_framework import permissions, viewsets
from django_tenants.utils import get_tenant_model
from client_app.models import Store,Product,Sale

from client_app.serializers import (
    RolesRetrieveSerializer,
    RolesCreateSerializer,
    RolesUpdateSerializer,
    StoresCreateSerializer,
    StoresRetrieveSerializer,
    ProductsCreateSerializer,
    ProductsRetrieveSerializer,
    SalesCreateSerializer,
    SalesRetrieveSerializer,
    CustomerSerializer
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
    
    def get_store_object(self,*args, **kwargs):
        tenant_model = get_tenant_model()
        tenant = tenant_model.objects.get(domain_url=self.request.tenant.domain_url)
        store_id = kwargs.get("store_id")
        try:
            return Store.objects.get(id=store_id,vendor=tenant,creator_id=self.get_logged_in_user_id(),is_deleted=False)
        except Store.DoesNotExist:
            return None
        
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_store_object(*args, **kwargs)
        if not instance:
            return Response({"message": "Store not found"}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = self.get_serializer(instance)
        return Response({"data":serializer.data})

    def partial_update(self, request, *args, **kwargs):

        instance = self.get_store_object(*args, **kwargs)
        if not instance:
            return Response({"message": "Store not found"}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()   
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_store_object(*args, **kwargs)
        if not instance:
            return Response({"message": "Store not found"}, status=status.HTTP_404_NOT_FOUND)
        instance.is_deleted = True
        instance.save()
        return Response(status=status.HTTP_204_NO_CONTENT)
    

class ProductViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows client to be viewed or edited.
    """
    queryset = Product.objects.filter(is_deleted=False)
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ProductsRetrieveSerializer
    pagination_class = CustomPagination

    def get_logged_in_user_id(self):
        return self.request.user.id

    def get_serializer_class(self,*args,**kwargs):
        if self.action in ['create','update']:
            return ProductsCreateSerializer
        return ProductsRetrieveSerializer
    
    def get_store_object(self,*args, **kwargs):
        tenant_model = get_tenant_model()
        tenant = tenant_model.objects.get(domain_url=self.request.tenant.domain_url)
        store_id = kwargs.get("store_id")
        try:
            return Store.objects.get(id=store_id,vendor=tenant,is_deleted=False)
        except Store.DoesNotExist:
            return None

    def create(self, request, *args, **kwargs):
        store = self.get_store_object(*args, **kwargs)
        if not store:
            return Response({"message": "Store not found"}, status=status.HTTP_404_NOT_FOUND)
        
        serializer_class = self.get_serializer_class()
        serializer = serializer_class(data=request.data)
        response_data = {}
        if serializer.is_valid():
            product = Product.objects.create(
                name=serializer.data["name"],
                type=serializer.data["type"],
                manufacturer=serializer.data["manufacturer"],
                price=serializer.data["price"],
                units_available=serializer.data["units_available"],
            )
            product.store = store
            product.save()
            response_data["status"] = True
            response_data["message"] = 'Product created successfully!'
            response_data["data"] = serializer.data
            return Response(response_data, status=status.HTTP_201_CREATED)
        response_data["status"] = False
        response_data["message"] = serializer.error_messages
        response_data["data"] = serializer.errors
        return Response(response_data, status=status.HTTP_400_BAD_REQUEST)
    
    def list(self, request, *args, **kwargs):
        store = self.get_store_object(*args, **kwargs)
        if not store:
            return Response({"message": "Store not found"}, status=status.HTTP_404_NOT_FOUND)
        queryset = Product.objects.filter(store=store,is_deleted=False)
        page = self.paginate_queryset(queryset)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(data=serializer.data)
    

    def retrieve(self, request, *args, **kwargs):
        store = self.get_store_object(*args, **kwargs)
        if not store:
            return Response({"message": "Store not found"}, status=status.HTTP_404_NOT_FOUND)
        try:
            instance = Product.objects.get(store=store,id=self.kwargs.get("product_id"),is_deleted=False)
        except Product.DoesNotExist:
            return Response({"message":"Product not Found"},status=status.HTTP_404_NOT_FOUND)
        
        serializer = self.get_serializer(instance)
        return Response({"data":serializer.data})

    def partial_update(self, request, *args, **kwargs):
        store = self.get_store_object(*args, **kwargs)
        if not store:
            return Response({"message": "Store not found"}, status=status.HTTP_404_NOT_FOUND)
        try:
            instance = Product.objects.get(store=store,id=self.kwargs.get("product_id"),is_deleted=False)
        except Product.DoesNotExist:
            return Response({"message": "Product not found"}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()   
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        store = self.get_store_object(*args, **kwargs)
        if not store:
            return Response({"message": "Store not found"}, status=status.HTTP_404_NOT_FOUND)
        try:
            instance = Product.objects.get(store=store,id=self.kwargs.get("product_id"),is_deleted=False)
        except Product.DoesNotExist:
            return Response({"message":"Product has already deleted"},status=status.HTTP_404_NOT_FOUND)
        
        instance.is_deleted = True
        instance.save()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
class SaleViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows client to be viewed or edited.
    """
    queryset = Sale.objects.filter(is_deleted=False)
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = SalesRetrieveSerializer
    pagination_class = CustomPagination

    def get_logged_in_user_id(self):
        return self.request.user.id

    def get_serializer_class(self,*args,**kwargs):
        if self.action in ['create','update']:
            return SalesCreateSerializer
        return SalesRetrieveSerializer
    
    def get_store_object(self,*args, **kwargs):
        tenant_model = get_tenant_model()
        tenant = tenant_model.objects.get(domain_url=self.request.tenant.domain_url)
        store_id = kwargs.get("store_id")
        try:
            return Store.objects.get(id=store_id,vendor=tenant,is_deleted=False)
        except Store.DoesNotExist:
            return None
        
    def get_product_object(self,*args, **kwargs):

        product_id = kwargs.get("product_id")
        try:
            return Product.objects.get(id=product_id,is_deleted=False)
        except Product.DoesNotExist:
            return None

    def create(self, request, *args, **kwargs):
        product = self.get_product_object(product_id=request.data["product_id"])
        if not product:
            return Response({"message": "Product not found"}, status=status.HTTP_404_NOT_FOUND)
        
        serializer_class = self.get_serializer_class()
        serializer = serializer_class(data=request.data)
        response_data = {}
        if serializer.is_valid():
           
            sale = Sale.objects.create(
                product=product,
                units_sold=serializer.data["units_sold"],
            )
            sale.salesperson_id = self.get_logged_in_user_id()
            sale.save()
            response_data["status"] = True
            response_data["message"] = 'Sales added successfully!'
            response_data["data"] = serializer.data
            return Response(response_data, status=status.HTTP_201_CREATED)
        response_data["status"] = False
        response_data["message"] = serializer.error_messages
        response_data["data"] = serializer.errors
        return Response(response_data, status=status.HTTP_400_BAD_REQUEST)
    
    def list(self, request, *args, **kwargs):
        salesperson = BaseCustomUser.objects.get(id=self.get_logged_in_user_id())
        queryset = Sale.objects.filter(salesperson=salesperson,is_deleted=False)
        page = self.paginate_queryset(queryset)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(data=serializer.data)

from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate

class CustomerViewSet(viewsets.ModelViewSet):

    def create(self, request, *args, **kwargs):
        serializer_class = CustomerSerializer
        serializer = serializer_class(data=request.data)
        response_data = {}
        if serializer.is_valid():
            user = BaseCustomUser.objects.create_user(
                name=f"{request.data['first_name']} {request.data['last_name']}",
                email=request.data["email"],
                password=request.data["password"],
                role=BaseCustomUser.Role.CUSTOMER,
                is_staff=True,
                is_active=True,
                is_superuser=False
                )
            user.save()
            
            response_data["status"] = True
            response_data["message"] = 'User Registered successfully!'
            response_data["data"] = serializer.data
            return Response(response_data, status=status.HTTP_201_CREATED)
        response_data["status"] = False
        response_data["message"] = ""
        response_data["data"] = serializer.errors
        return Response(response_data, status=status.HTTP_400_BAD_REQUEST)
    
    def login(self, request, *args, **kwargs):
        email = request.data.get('email')
        password = request.data.get('password')

        if email and password:
            user = authenticate(request, email=email, password=password)
            if user:
                refresh = RefreshToken.for_user(user)
                return Response({
                    'access_token': str(refresh.access_token),
                    'refresh_token': str(refresh),
                }, status=status.HTTP_200_OK)
            else:
                return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
        else:
            return Response({'error': 'Both email and password are required'}, status=status.HTTP_400_BAD_REQUEST)
        
class CustomerStoresViewSet(viewsets.ModelViewSet):
    queryset = Store.objects.filter(is_deleted=False)
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = StoresRetrieveSerializer
    pagination_class = CustomPagination

    def get_stores(self, request, *args, **kwargs):
        queryset = Store.objects.filter(is_deleted=False)
        page = self.paginate_queryset(queryset)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(data=serializer.data)
    
    
    def get_store_products(self, request, *args, **kwargs):
        store_id = kwargs.get("store_id")
        try:
            store = Store.objects.get(id=store_id)
        except Store.DoesNotExist:
            return Response({"message":"Store Not found"},status=status.HTTP_404_NOT_FOUND)
        
        queryset = Product.objects.filter(is_deleted=False,store=store)
        page = self.paginate_queryset(queryset)
        serializer = ProductsRetrieveSerializer(page, many=True)
        return self.get_paginated_response(data=serializer.data)

    def get_store_object(self,*args, **kwargs):
        tenant_model = get_tenant_model()
        tenant = tenant_model.objects.get(domain_url=self.request.tenant.domain_url)
        store_id = kwargs.get("store_id")
        try:
            return Store.objects.get(id=store_id,vendor=tenant,is_deleted=False)
        except Store.DoesNotExist:
            return None
        
    def get_store(self, request, *args, **kwargs):
        instance = self.get_store_object(*args, **kwargs)
        if not instance:
            return Response({"message": "Store not found"}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = self.get_serializer(instance)
        return Response({"data":serializer.data})
    

class CustomerProductsViewSet(viewsets.ModelViewSet):
    queryset = Store.objects.filter(is_deleted=False)
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ProductsRetrieveSerializer
    pagination_class = CustomPagination

    def get_products(self, request, *args, **kwargs):
        queryset = Product.objects.filter(is_deleted=False)
        page = self.paginate_queryset(queryset)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(data=serializer.data)

    def get_product(self, request, *args, **kwargs):
        product_id = kwargs.get("product_id")
        try:
            instance = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response({"message": "Store not found"}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = self.get_serializer(instance)
        return Response({"data":serializer.data})