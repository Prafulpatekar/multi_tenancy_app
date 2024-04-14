from .models import Client
from rest_framework import serializers



class VendorCreateSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Client
        fields = ['vendor_name','description']


class VendorRetrieveSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Client
        fields = ['id','vendor_name','schema_name','vendor_uuid','created_on','domain_url','description']
    
# class RolesRetrieveSerializer(serializers.HyperlinkedModelSerializer):
#     class Meta:
#         model = BaseCustomUser
#         fields = ['id','email','role','name']

# class RolesCreateSerializer(serializers.HyperlinkedModelSerializer):
#     class Meta:
#         model = BaseCustomUser
#         fields = ['name','email','role','password']
# class RolesUpdateSerializer(serializers.HyperlinkedModelSerializer):
#     class Meta:
#         model = BaseCustomUser
#         fields = ['name']