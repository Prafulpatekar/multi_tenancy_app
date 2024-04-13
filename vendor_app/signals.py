from django.db.models.signals import pre_save
from django.dispatch import receiver
from vendor_app.models import Client

@receiver(pre_save, sender=Client)
def update_schema_name(sender, instance, **kwargs):
    if instance._state.adding:
        name = instance.name
        schema_name = name.lower().replace(" ", "")
        instance.schema_name = schema_name