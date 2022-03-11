# Generated by Django 3.2.9 on 2022-03-09 19:36

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('base_app', '0043_delete_clients_email'),
        ('user', '0003_movers_password_recovery_codes'),
    ]

    operations = [
        migrations.CreateModel(
            name='Quote_Request_Payment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ref', models.CharField(max_length=30)),
                ('amount', models.DecimalField(decimal_places=2, max_digits=5)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('status', models.BooleanField(default=False)),
                ('mover_quote_request', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='base_app.mover_quote_request')),
            ],
        ),
    ]
