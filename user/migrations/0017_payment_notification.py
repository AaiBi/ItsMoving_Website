# Generated by Django 3.2.9 on 2022-03-25 18:33

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('base_app', '0045_alter_mover_quote_request_paid'),
        ('user', '0016_delete_quote_request_payment'),
    ]

    operations = [
        migrations.CreateModel(
            name='Payment_Notification',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('mover', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='base_app.mover')),
            ],
        ),
    ]
