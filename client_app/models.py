from django.contrib.auth.models import BaseUserManager
from django.db import models
from vendor_app.models import BaseCustomUser,Client


class AdminManager(BaseUserManager):
    def get_queryset(self, *args, **kwargs):
        results = super().get_queryset(*args, **kwargs)
        return results.filter(role=BaseCustomUser.Role.ADMIN)
    
    def create_user(self, email, password=None, **extra_fields):
        """
        Creates and saves a regular user with the given email and password.
        """
        extra_fields.setdefault('role', BaseCustomUser.Role.ADMIN)
        return self._create_user(email, password, **extra_fields)

    def _create_user(self, email, password=None, **extra_fields):
        """
        Creates and saves a regular user with the given email and password.
        """
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    

class Admin(BaseCustomUser):
    base_role = BaseCustomUser.Role.ADMIN
    objects = AdminManager()

    class Meta:
        proxy = True

class SupervisorManager(BaseUserManager):
    def get_queryset(self, *args, **kwargs):
        results = super().get_queryset(*args, **kwargs)
        return results.filter(role=BaseCustomUser.Role.SUPERVISOR)

class Supervisor(BaseCustomUser):
    base_role = BaseCustomUser.Role.SUPERVISOR
    objects = SupervisorManager()

    class Meta:
        proxy = True

class SalesPersonManager(BaseUserManager):
    def get_queryset(self, *args, **kwargs):
        results = super().get_queryset(*args, **kwargs)
        return results.filter(role=BaseCustomUser.Role.SALES_PERSION)


class SalesPerson(BaseCustomUser):
    base_role = BaseCustomUser.Role.SALES_PERSION
    objects = SalesPersonManager()

    class Meta:
        proxy = True

class CustomerManager(BaseUserManager):
    def get_queryset(self, *args, **kwargs):
        results = super().get_queryset(*args, **kwargs)
        return results.filter(role=BaseCustomUser.Role.SALES_PERSION)


class Customer(BaseCustomUser):
    base_role = BaseCustomUser.Role.CUSTOMER
    objects = CustomerManager()
    
    class Meta:
        proxy = True

class Store(models.Model):
    name = models.CharField(max_length=100, null=False, blank=False)
    location = models.CharField(max_length=100, null=False, blank=False)
    contact = models.CharField(max_length=100, null=False, blank=False)
    is_deleted = models.BooleanField(default=False)
    vendor = models.ForeignKey(Client, on_delete=models.SET_NULL,null=True, related_name='vendor')
    creator = models.ForeignKey(BaseCustomUser, on_delete=models.SET_NULL,null=True, related_name='creator')


class Product(models.Model):
    name = models.CharField(max_length=100, null=False, blank=False)
    type = models.CharField(max_length=100, null=False, blank=False)
    manufacturer = models.CharField(max_length=100, null=False, blank=False)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=False, blank=False)
    units_available = models.PositiveIntegerField(default=0)
    is_deleted = models.BooleanField(default=False)
    store = models.ForeignKey(Store, on_delete=models.SET_NULL,null=True)

class Sale(models.Model):
    product = models.ForeignKey(Product, on_delete=models.SET_NULL,null=True,related_name='product')
    salesperson = models.ForeignKey(SalesPerson, on_delete=models.SET_NULL,null=True,related_name='salesperson')
    units_sold = models.PositiveIntegerField()
    is_deleted = models.BooleanField(default=False)
    sale_date = models.DateField(auto_now_add=True)
