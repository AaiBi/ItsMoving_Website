# Generated by Django 3.2.9 on 2022-06-13 18:56

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('base_app', '0054_remove_quote_request_email_sent_to_customer'),
    ]

    operations = [
        migrations.CreateModel(
            name='Customers_Notification_Email',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('quote_request_distributed', models.BooleanField(default=False)),
                ('quote_request_not_distributed', models.BooleanField(default=False)),
                ('mover', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='base_app.mover')),
                ('quote_request', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='base_app.quote_request')),
            ],
        ),
    ]
