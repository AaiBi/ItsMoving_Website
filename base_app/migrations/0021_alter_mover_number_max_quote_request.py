# Generated by Django 3.2.9 on 2022-02-21 19:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base_app', '0020_quote_request_distributed'),
    ]

    operations = [
        migrations.AlterField(
            model_name='mover',
            name='number_max_quote_request',
            field=models.IntegerField(default=1),
        ),
    ]
