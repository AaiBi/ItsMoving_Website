# Generated by Django 3.2.9 on 2022-03-08 20:01

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('base_app', '0035_alter_mover_number_max_quote_request'),
    ]

    operations = [
        migrations.CreateModel(
            name='User_Emails',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('mover_quote_request', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='base_app.mover_quote_request')),
            ],
        ),
    ]