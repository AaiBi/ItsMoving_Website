# Generated by Django 3.2.9 on 2022-03-09 17:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base_app', '0039_movers_email_mover'),
    ]

    operations = [
        migrations.AddField(
            model_name='quote_request',
            name='email_sent_to_customer',
            field=models.BooleanField(default=False),
        ),
    ]
