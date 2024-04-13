from django.db import models
from django_tenants.models import TenantMixin,DomainMixin
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone

class Client(TenantMixin):
    name = models.CharField(max_length=100,null=False,blank=False)
    schema_name = models.CharField(max_length=100,null=False,blank=False)
    created_date = models.DateField(auto_now_add=True)
    created_datetime = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.name


class Domain(DomainMixin):
    pass


class CustomUserManager(BaseUserManager):
    def create_user(self, email, role, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, role=role, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('role', BaseCustomUser.Role.ADMIN)
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('role') !=  BaseCustomUser.Role.ADMIN:
            raise ValueError(f'Superuser must have role "{BaseCustomUser.Role.ADMIN}".')

        return self.create_user(email, password=password, **extra_fields)

class BaseCustomUser(AbstractBaseUser, PermissionsMixin):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)
    client = models.ForeignKey(Client, on_delete=models.SET_NULL, related_name='roles',null=True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['role']

    class Role(models.TextChoices):
        ADMIN = "ADMIN", "Admin"
        SUPERVISOR = "SUPERVISOR", "Supervisor"
        SALES_PERSION = "SALES_PERSON", "Sales Person"
        CUSTOMER = "CUSTOMER", "CUSTOMER"

    base_role = Role.CUSTOMER

    role = models.CharField(max_length=50, choices=Role.choices)

    def __str__(self):
        return self.email


class AdminManager(BaseUserManager):
    def get_queryset(self, *args, **kwargs):
        results = super().get_queryset(*args, **kwargs)
        return results.filter(role=BaseCustomUser.Role.ADMIN)

class Admin(BaseCustomUser):
    base_role = BaseCustomUser.Role.ADMIN
    objects = AdminManager()

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault('role', BaseCustomUser.Role.ADMIN)
        return self.__class__.objects.create_user(email, password=password, **extra_fields)
    
    class Meta:
        verbose_name = 'Admin'
        verbose_name_plural = 'Admins'

class SupervisorManager(BaseUserManager):
    def get_queryset(self, *args, **kwargs):
        results = super().get_queryset(*args, **kwargs)
        return results.filter(role=BaseCustomUser.Role.SUPERVISOR)

class Supervisor(BaseCustomUser):
    base_role = BaseCustomUser.Role.SUPERVISOR
    objects = SupervisorManager()

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault('role', BaseCustomUser.Role.SUPERVISOR)
        return self.__class__.objects.create_user(email, password=password, **extra_fields)
    
    class Meta:
        verbose_name = 'Supervisor'
        verbose_name_plural = 'Supervisors'

class SalesPersonManager(BaseUserManager):
    def get_queryset(self, *args, **kwargs):
        results = super().get_queryset(*args, **kwargs)
        return results.filter(role=BaseCustomUser.Role.SALES_PERSION)


class SalesPerson(BaseCustomUser):
    base_role = BaseCustomUser.Role.SALES_PERSION
    objects = SalesPersonManager()

    def create_user(self, email, password=None, client=None, **extra_fields):
        extra_fields.setdefault('role', BaseCustomUser.Role.SALES_PERSION)
        if client is not None:
            extra_fields['client'] = client
        return self.__class__.objects.create_user(email, password=password, **extra_fields)

    class Meta:
        verbose_name = 'Sales Person'
        verbose_name_plural = 'Sales People'

class CustomerManager(BaseUserManager):
    def get_queryset(self, *args, **kwargs):
        results = super().get_queryset(*args, **kwargs)
        return results.filter(role=BaseCustomUser.Role.SALES_PERSION)


class Customer(BaseCustomUser):
    base_role = BaseCustomUser.Role.CUSTOMER
    objects = CustomerManager()

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault('role', BaseCustomUser.Role.CUSTOMER)
        return self.__class__.objects.create_user(email, password=password, **extra_fields)
    
    class Meta:
        proxy = True
