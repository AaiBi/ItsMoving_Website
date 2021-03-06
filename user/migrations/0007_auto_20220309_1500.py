# Generated by Django 3.2.9 on 2022-03-09 20:00

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0006_alter_quote_request_payment_amount'),
    ]

    operations = [
        migrations.CreateModel(
            name='Payment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.DecimalField(decimal_places=2, default=6.5, max_digits=5)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('tva', models.DecimalField(decimal_places=2, default=1.365, max_digits=5)),
            ],
        ),
        migrations.RemoveField(
            model_name='quote_request_payment',
            name='amount',
        ),
        migrations.RemoveField(
            model_name='quote_request_payment',
            name='tva',
        ),
        migrations.AddField(
            model_name='quote_request_payment',
            name='payment',
            field=models.ForeignKey(default='', on_delete=django.db.models.deletion.CASCADE, to='user.payment'),
        ),
    ]
