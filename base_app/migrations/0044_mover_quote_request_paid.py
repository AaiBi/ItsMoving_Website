# Generated by Django 3.2.9 on 2022-03-11 20:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base_app', '0043_delete_clients_email'),
    ]

    operations = [
        migrations.AddField(
            model_name='mover_quote_request',
            name='paid',
            field=models.BooleanField(default=False),
        ),
    ]
