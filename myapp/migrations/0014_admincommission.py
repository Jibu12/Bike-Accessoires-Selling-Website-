# Generated by Django 5.0.4 on 2024-05-12 06:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0013_orderitem'),
    ]

    operations = [
        migrations.CreateModel(
            name='AdminCommission',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('commission_rate', models.DecimalField(decimal_places=2, default=0.0, max_digits=5)),
            ],
        ),
    ]