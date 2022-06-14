# Generated by Django 3.2.9 on 2022-06-06 03:13

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('base_app', '0045_alter_mover_quote_request_paid'),
    ]

    operations = [
        migrations.CreateModel(
            name='Region',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=300)),
                ('country', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='base_app.country')),
            ],
        ),
    ]
