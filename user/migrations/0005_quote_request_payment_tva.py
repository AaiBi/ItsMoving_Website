# Generated by Django 3.2.9 on 2022-03-09 19:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0004_quote_request_payment'),
    ]

    operations = [
        migrations.AddField(
            model_name='quote_request_payment',
            name='tva',
            field=models.DecimalField(decimal_places=2, default=1.365, max_digits=5),
        ),
    ]
