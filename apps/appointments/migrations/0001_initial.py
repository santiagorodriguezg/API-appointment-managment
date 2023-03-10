# Generated by Django 3.2.8 on 2021-11-06 16:20

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


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
                ('type', models.CharField(max_length=7, verbose_name='tipo de cita')),
                ('children', models.JSONField(blank=True, null=True, verbose_name='datos de los hijos')),
                ('aggressor', models.JSONField(blank=True, null=True, verbose_name='datos del agresor')),
                ('description', models.TextField(blank=True, null=True, verbose_name='descripción')),
                ('audio', models.FileField(upload_to='appointments/audio', validators=[django.core.validators.FileExtensionValidator(allowed_extensions=['mp3', 'mp4', 'ogg', 'm4a'])], verbose_name='audio')),
                ('start_date', models.DateTimeField(blank=True, null=True, verbose_name='fecha de inicio')),
                ('end_date', models.DateTimeField(blank=True, null=True, verbose_name='fecha de finalización')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='fecha de registro')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='fecha de actualización')),
                ('doctors', models.ManyToManyField(blank=True, related_name='doctors', to=settings.AUTH_USER_MODEL, verbose_name='doctores')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='patient', to=settings.AUTH_USER_MODEL, verbose_name='user')),
            ],
            options={
                'verbose_name': 'cita',
                'verbose_name_plural': 'citas',
                'db_table': 'appointment',
                'permissions': [('add_appointment_from_me', 'Can add my appointments'), ('change_appointment_from_me', 'Can change my appointments'), ('delete_appointment_from_me', 'Can delete my appointments'), ('view_appointment_from_me', 'Can view my appointments')],
            },
        ),
        migrations.CreateModel(
            name='AppointmentMultimedia',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file', models.FileField(upload_to='appointments/files', validators=[django.core.validators.FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png', 'webp', 'pdf'])], verbose_name='archivo')),
                ('file_type', models.CharField(choices=[('PDF', 'Archivo PDF'), ('IMG', 'Imagen'), ('VIDEO', 'Video')], max_length=8, verbose_name='tipo de archivo')),
                ('appointment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='multimedia', to='appointments.appointment', verbose_name='cita')),
            ],
            options={
                'verbose_name': 'archivo de la cita',
                'verbose_name_plural': 'archivos de las citas',
                'db_table': 'appointment_multimedia',
            },
        ),
    ]
