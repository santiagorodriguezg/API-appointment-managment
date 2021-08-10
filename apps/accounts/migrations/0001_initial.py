# Generated by Django 3.2.6 on 2021-08-10 02:13

import django.contrib.auth.validators
import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('role', models.CharField(choices=[('ADMIN', 'Administrador'), ('DOC', 'Doctor'), ('USR', 'Usuario')], default='USR', max_length=8, verbose_name='tipo de usuario')),
                ('first_name', models.CharField(max_length=60, validators=[django.core.validators.MinLengthValidator(limit_value=2, message='El nombre debe tener al menos 2 caracteres.'), django.core.validators.RegexValidator(code='invalid_first_name', message='El nombre debe tener solo letras (A-Z).', regex='^[a-zA-ZÁ-ÿ+ ?]*$')], verbose_name='nombre')),
                ('last_name', models.CharField(blank=True, max_length=60, null=True, validators=[django.core.validators.MinLengthValidator(limit_value=2, message='Sus apellidos deben tener al menos 2 caracteres.'), django.core.validators.RegexValidator(code='invalid_last_name', message='Sus apellidos deben tener solo letras (A-Z).', regex='^[a-zA-ZÁ-ÿ+ ?]*$')], verbose_name='apellidos')),
                ('identification_type', models.CharField(choices=[('CC', 'Cédula de Ciudadanía'), ('CE', 'Cédula de Extranjería')], default='CC', max_length=2, verbose_name='tipo de identificación')),
                ('identification_number', models.CharField(error_messages={'unique': 'Ya existe un usuario con este número de identificación.'}, max_length=10, unique=True, validators=[django.core.validators.MinLengthValidator(limit_value=6, message='Su identificación debe tener al menos 6 caracteres.')], verbose_name='número de identificación')),
                ('username', models.CharField(error_messages={'unique': 'Ya existe un usuario con este nombre de usuario.'}, help_text='Su usuario debe tener máximo 60 caracteres. Letras, dígitos y @/./+/-/_ solamente.', max_length=60, unique=True, validators=[django.contrib.auth.validators.UnicodeUsernameValidator()], verbose_name='usuario')),
                ('email', models.EmailField(blank=True, error_messages={'unique': 'Ya existe un contacto con este correo electrónico.'}, max_length=60, null=True, verbose_name='correo electrónico')),
                ('phone', models.CharField(max_length=12, verbose_name='teléfono')),
                ('picture', models.ImageField(blank=True, null=True, upload_to='users/pictures', validators=[django.core.validators.FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png', 'webp'])], verbose_name='foto de perfil')),
                ('city', models.CharField(max_length=60, validators=[django.core.validators.RegexValidator(code='invalid_city', message='El nombre de la ciudad debe tener solo letras (A-Z).', regex='^[a-zA-ZÁ-ÿ+ ?]*$')], verbose_name='ciudad')),
                ('neighborhood', models.CharField(blank=True, max_length=40, null=True, validators=[django.core.validators.RegexValidator(code='invalid_city', message='El nombre del barrio debe tener solo letras (A-Z).', regex='^[a-zA-ZÁ-ÿ+ ?]*$')], verbose_name='barrio')),
                ('address', models.CharField(blank=True, max_length=60, null=True, verbose_name='dirección')),
                ('is_active', models.BooleanField(default=True, help_text='Indica que la cuenta del usuario está activa.', verbose_name='activo')),
                ('is_staff', models.BooleanField(default=False, help_text='Designa si este usuario puede acceder al sitio de administración.', verbose_name='login en admin')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='fecha de registro')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='fecha de actualización')),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.Group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.Permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': 'usuario',
                'verbose_name_plural': 'usuarios',
                'db_table': 'user',
                'permissions': [('password_rest', 'Generate password reset link')],
            },
        ),
    ]
