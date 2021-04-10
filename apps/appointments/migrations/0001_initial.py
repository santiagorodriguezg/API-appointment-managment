# Generated by Django 3.2 on 2021-04-10 23:20

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Appointment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('children', models.JSONField(blank=True, null=True, verbose_name='hijos')),
                ('aggressor', models.CharField(blank=True, max_length=500, null=True, verbose_name='datos del posible agresor')),
                ('start_time', models.DateTimeField(blank=True, null=True, verbose_name='fecha de inicio')),
                ('end_time', models.DateTimeField(blank=True, null=True, verbose_name='fecha de finalización')),
                ('description', models.TextField(blank=True, null=True, verbose_name='descripción')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='fecha de registro')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='fecha de modificación de la cuenta')),
                ('doctor', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='doctor', to=settings.AUTH_USER_MODEL, verbose_name='doctor')),
                ('patient', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='patient', to=settings.AUTH_USER_MODEL, verbose_name='paciente')),
            ],
            options={
                'verbose_name': 'cita',
                'verbose_name_plural': 'citas',
                'db_table': 'appointment',
            },
        ),
    ]
