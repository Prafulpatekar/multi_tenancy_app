from django.db import models
from django_tenants.models import TenantMixin,DomainMixin
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils import timezone
import uuid
import os


class Client(TenantMixin):
    vendor_name = models.CharField(max_length=100, unique=True, null=False, blank=False)
    vendor_uuid = models.UUIDField(default=uuid.uuid4,auto_created=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)
    description = models.TextField(blank=True)
    domain_url = models.URLField(blank=True, null=True, default=os.getenv("DOMAIN"))
    schema_name = models.CharField(max_length=100,null=False,blank=False)
    is_active = models.BooleanField(default=True, blank=True)
    created_on = models.DateField(auto_now_add=True)

    # default true, schema will be automatically created and
    # synced when it is saved
    auto_create_schema = True

    """
    USE THIS WITH CAUTION!
    Set this flag to true on a parent class if you want the schema to be
    automatically deleted if the tenant row gets deleted.
    """
    auto_drop_schema = True


    class Meta:
        ordering = ('-updated_at',)

    def __str__(self):
        return f"{self.vendor_name}"

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

        return self.create_user(email, password=password, **extra_fields)

class BaseCustomUser(AbstractBaseUser, PermissionsMixin):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
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