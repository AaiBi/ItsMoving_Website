# Generated by Django 3.2.9 on 2022-07-20 20:04

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('base_app', '0056_auto_20220613_1650'),
    ]

    operations = [
        migrations.RenameField(
            model_name='mover',
            old_name='validated',
            new_name='pause',
        ),
    ]
