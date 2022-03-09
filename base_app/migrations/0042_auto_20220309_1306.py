# Generated by Django 3.2.9 on 2022-03-09 18:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base_app', '0041_auto_20220309_1249'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='mover_quote_request',
            name='email_sent_to_customer',
        ),
        migrations.AddField(
            model_name='quote_request',
            name='email_sent_to_customer',
            field=models.BooleanField(default=False),
        ),
    ]
