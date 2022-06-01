# Generated by Django 3.2.9 on 2022-05-21 19:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0017_payment_notification'),
    ]

    operations = [
        migrations.AlterField(
            model_name='payment',
            name='amount',
            field=models.DecimalField(decimal_places=2, default=5, max_digits=5),
        ),
        migrations.AlterField(
            model_name='payment',
            name='tva',
            field=models.DecimalField(decimal_places=2, default=1.05, max_digits=5),
        ),
    ]
