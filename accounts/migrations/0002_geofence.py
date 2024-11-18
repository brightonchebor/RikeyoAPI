# Generated by Django 5.0.6 on 2024-11-18 16:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Geofence',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('office_lat', models.IntegerField()),
                ('office_long', models.IntegerField()),
                ('geofence_radius', models.IntegerField()),
            ],
        ),
    ]
