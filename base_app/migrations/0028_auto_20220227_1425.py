# Generated by Django 3.2.9 on 2022-02-27 19:25

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('base_app', '0027_number_distribution_quote_request'),
    ]

    operations = [
        migrations.AddField(
            model_name='mover_quote_request',
            name='treated',
            field=models.BooleanField(default=False),
        ),
        migrations.CreateModel(
            name='Quote_Request_Rejected',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('reason', models.TextField()),
                ('quote_request', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='base_app.quote_request')),
            ],
        ),
    ]
