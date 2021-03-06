# Generated by Django 3.2.9 on 2022-02-08 18:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base_app', '0003_quote_request_user'),
    ]

    operations = [
        migrations.AddField(
            model_name='quote_request',
            name='email',
            field=models.EmailField(default='', max_length=254),
        ),
        migrations.AddField(
            model_name='quote_request',
            name='firstname',
            field=models.CharField(default='', max_length=300),
        ),
        migrations.AddField(
            model_name='quote_request',
            name='lastname',
            field=models.CharField(default='', max_length=300),
        ),
        migrations.AddField(
            model_name='quote_request',
            name='phone_number',
            field=models.CharField(default='', max_length=30),
        ),
        migrations.AddField(
            model_name='quote_request',
            name='social_reason',
            field=models.TextField(default=''),
        ),
    ]
