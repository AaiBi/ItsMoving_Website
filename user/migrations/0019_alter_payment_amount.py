# Generated by Django 3.2.9 on 2022-05-21 20:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0018_auto_20220521_1540'),
    ]

    operations = [
        migrations.AlterField(
            model_name='payment',
            name='amount',
            field=models.DecimalField(decimal_places=2, default=4.99, max_digits=5),
        ),
    ]
