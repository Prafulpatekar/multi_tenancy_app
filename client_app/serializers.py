from vendor_app.models import BaseCustomUser,Client
from client_app.models import Store
from rest_framework import serializers



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