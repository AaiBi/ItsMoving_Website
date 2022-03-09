# Generated by Django 3.2.9 on 2022-03-09 17:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base_app', '0040_quote_request_email_sent_to_customer'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='quote_request',
            name='email_sent_to_customer',
        ),
        migrations.AddField(
            model_name='mover_quote_request',
            name='email_sent_to_customer',
            field=models.BooleanField(default=False),
        ),
    ]
