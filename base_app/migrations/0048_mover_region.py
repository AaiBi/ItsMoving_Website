# Generated by Django 3.2.9 on 2022-06-06 03:37

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('base_app', '0047_remove_mover_city'),
    ]

    operations = [
        migrations.AddField(
            model_name='mover',
            name='region',
            field=models.ForeignKey(default='', on_delete=django.db.models.deletion.CASCADE, to='base_app.region'),
        ),
    ]
