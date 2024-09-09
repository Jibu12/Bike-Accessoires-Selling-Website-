# Generated by Django 5.0.4 on 2024-05-16 04:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0014_admincommission'),
    ]

    operations = [
        migrations.AddField(
            model_name='admincommission',
            name='total_commission_amount',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=10),
        ),
        migrations.AddField(
            model_name='orderitem',
            name='expected_delivery_date',
            field=models.DateField(blank=True, null=True),
        ),
    ]