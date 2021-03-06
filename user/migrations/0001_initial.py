# Generated by Django 3.2.9 on 2022-01-25 17:00

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='User_Info',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('indicatif', models.CharField(default='', max_length=5)),
                ('phone_number', models.CharField(max_length=50)),
                ('Adresse', models.CharField(max_length=300)),
                ('country', models.CharField(max_length=300)),
                ('activated', models.BooleanField(default=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('profil_picture', models.ImageField(blank=True, upload_to='user/images/profil_image/')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
