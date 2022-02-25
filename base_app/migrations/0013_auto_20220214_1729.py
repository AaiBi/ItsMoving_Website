# Generated by Django 3.2.9 on 2022-02-14 22:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base_app', '0012_mover_quote_request'),
    ]

    operations = [
        migrations.AddField(
            model_name='quote_request',
            name='Country_Arrival',
            field=models.CharField(default='', max_length=300),
        ),
        migrations.AddField(
            model_name='quote_request',
            name='Country_Departure',
            field=models.CharField(default='', max_length=300),
        ),
    ]