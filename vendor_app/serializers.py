from .models import Client,BaseCustomUser
from rest_framework import serializers



class VendorCreateSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Client
        fields = ['name']


class VendorRetrieveSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Client
        fields = ['id','name','schema_name','created_date','created_datetime']
    
class RolesRetrieveSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = BaseCustomUser
        fields = ['id','email','role']

class RolesCreateSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = BaseCustomUser
        fields = ['name','email','role','password']