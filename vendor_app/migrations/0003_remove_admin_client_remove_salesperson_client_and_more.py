# Generated by Django 5.0.4 on 2024-04-13 21:34

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vendor_app', '0002_delete_admin_delete_supervisor_admin_supervisor'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='admin',
            name='client',
        ),
        migrations.RemoveField(
            model_name='salesperson',
            name='client',
        ),
        migrations.RemoveField(
            model_name='supervisor',
            name='client',
        ),
        migrations.AddField(
            model_name='basecustomuser',
            name='client',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='vendor_app.client'),
        ),
    ]
