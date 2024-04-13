from django.db import models
from vendor_app.models import Client,SalesPerson

# Create your models here.

class Store(models.Model):
    name = models.CharField(max_length=100, null=False, blank=False)
    location = models.CharField(max_length=100, null=False, blank=False)
    contact_details = models.CharField(max_length=100, null=False, blank=False)

class Product(models.Model):
    name = models.CharField(max_length=100, null=False, blank=False)
    type = models.CharField(max_length=100, null=False, blank=False)
    manufacturer = models.CharField(max_length=100, null=False, blank=False)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=False, blank=False)
    units_available = models.PositiveIntegerField(default=0)
    store = models.ForeignKey(Store, on_delete=models.CASCADE)

class Sale(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    salesperson = models.ForeignKey(SalesPerson, on_delete=models.CASCADE)
    units_sold = models.PositiveIntegerField()
    sale_date = models.DateField(auto_now_add=True)
