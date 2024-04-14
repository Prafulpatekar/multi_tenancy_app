from django.db.models.signals import pre_save
from django.dispatch import receiver
from client_app.models import Sale,Product

@receiver(pre_save, sender=Sale)
def update_product_units(sender, instance, **kwargs):
    if instance._state.adding:
        product = Product.objects.get(id=instance.product.id)
        product.units_available -= instance.units_sold
        product.save()


"""
from vendor_app.models import Client,Domain                                                         
client = Client.objects.create(vendor_name="Public",schema_name="public",description="Public vendor for superadmin",domain_url="localhost")
"""