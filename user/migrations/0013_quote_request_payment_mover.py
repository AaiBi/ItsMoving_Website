# Generated by Django 3.2.9 on 2022-03-13 19:58

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('base_app', '0045_alter_mover_quote_request_paid'),
        ('user', '0012_auto_20220313_1555'),
    ]

    operations = [
        migrations.AddField(
            model_name='quote_request_payment',
            name='mover',
            field=models.ForeignKey(default='', on_delete=django.db.models.deletion.CASCADE, to='base_app.mover'),
        ),
    ]
