# Generated by Django 3.2.9 on 2022-03-09 19:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0005_quote_request_payment_tva'),
    ]

    operations = [
        migrations.AlterField(
            model_name='quote_request_payment',
            name='amount',
            field=models.DecimalField(decimal_places=2, default=6.5, max_digits=5),
        ),
    ]