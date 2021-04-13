# Generated by Django 3.2 on 2021-04-11 15:46

import django.core.validators
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
                ('description', models.TextField(blank=True, null=True, verbose_name='descripción')),
                ('audio', models.FileField(blank=True, null=True, upload_to='appointments/audio', validators=[django.core.validators.FileExtensionValidator(allowed_extensions=['mp3', 'mp4'])], verbose_name='audio')),
                ('start_time', models.DateTimeField(blank=True, null=True, verbose_name='fecha de inicio')),
                ('end_time', models.DateTimeField(blank=True, null=True, verbose_name='fecha de finalización')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='fecha de registro')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='fecha de modificación de la cuenta')),
                ('doctor', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='doctor', to=settings.AUTH_USER_MODEL, verbose_name='doctor')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='patient', to=settings.AUTH_USER_MODEL, verbose_name='user')),
            ],
            options={
                'verbose_name': 'cita',
                'verbose_name_plural': 'citas',
                'db_table': 'appointment',
            },
        ),
    ]
