from vendor_app.models import BaseCustomUser,Client
from client_app.models import Store,Product,Sale
from rest_framework import serializers
import re
from django.contrib.auth.password_validation import validate_password



class RolesRetrieveSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = BaseCustomUser
        fields = ['id','email','role','name']

class RolesCreateSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = BaseCustomUser
        fields = ['name','email','role','password']

class RolesUpdateSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = BaseCustomUser
        fields = ['name']


class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = BaseCustomUser
        fields = ['id', 'name', 'email']  # Add fields you want to display from Creator model

class VendorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = ['id', 'vendor_name', 'description']  # Add fields you want to display from Vendor model

class StoresRetrieveSerializer(serializers.ModelSerializer):
    creator = CustomUserSerializer(read_only=True)  # Use the CustomUserSerializer for creator field
    vendor = VendorSerializer(read_only=True)  # Use the VendorSerializer for vendor field

    class Meta:
        model = Store
        fields = ['id', 'name', 'location', 'contact', 'creator', 'vendor']

class StoresCreateSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Store
        fields = ['name','location','contact']


class ProductsRetrieveSerializer(serializers.ModelSerializer):
    store = StoresRetrieveSerializer(read_only=True)

    class Meta:
        model = Product
        fields = ['name', 'type', 'manufacturer', 'price', 'units_available', 'store']

class ProductsCreateSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Product
        fields = ['name', 'type', 'manufacturer', 'price', 'units_available']

class SalesRetrieveSerializer(serializers.ModelSerializer):
    product = ProductsRetrieveSerializer(read_only=True)
    store = StoresRetrieveSerializer(read_only=True)

    class Meta:
        model = Sale
        fields = ['units_sold','product','store']

class SalesCreateSerializer(serializers.ModelSerializer):
    product_id = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all(), source='product', write_only=True)

    class Meta:
        model = Sale
        fields = ['units_sold', 'product_id']



class CustomerSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    email = serializers.EmailField(required=True)
    first_name = serializers.CharField(max_length=100, required=True, allow_blank=False)
    last_name = serializers.CharField(max_length=100, required=True, allow_blank=False)

    def validate_password(self, value):
        # password validation
        if len(value) < 8 or len(value) > 12:
            raise serializers.ValidationError("Password must be between 8 and 12 characters long")
        if not any(char.isupper() for char in value):
            raise serializers.ValidationError("Password must contain at least one uppercase letter")
        if not any(char.isdigit() for char in value):
            raise serializers.ValidationError("Password must contain at least one digit")
        if not any(char in '!@#$%^&*()_+-=[]{}|;:,.<>?~' for char in value):
            raise serializers.ValidationError("Password must contain at least one special character")

        return value

    def validate_last_name(self, value):
        # last name validation
        if "'" not in value or value.count("'") > 1 or '.' not in value or value.count('.') > 1:
            raise serializers.ValidationError("Invalid last name format. It should contain one single quote and one dot.")

        return value

    def validate_email(self, value):
        # Email format validation
        if not re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', value):
            raise serializers.ValidationError("Invalid email format")

        # Email existence validation
        if BaseCustomUser.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email already exists")

        return value

    class Meta:
        model = BaseCustomUser
        fields = ['email', 'password', 'first_name', 'last_name']