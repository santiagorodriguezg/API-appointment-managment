# Generated by Django 3.1.7 on 2021-03-18 00:32

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Appointment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start_time', models.DateTimeField(blank=True, null=True, verbose_name='fecha de inicio')),
                ('end_time', models.DateTimeField(blank=True, null=True, verbose_name='fecha de finalización')),
                ('description', models.TextField(blank=True, null=True, verbose_name='descripción')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='fecha de registro')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='fecha de modificación de la cuenta')),
            ],
            options={
                'verbose_name': 'cita',
                'verbose_name_plural': 'citas',
                'db_table': 'appointment',
            },
        ),
    ]
