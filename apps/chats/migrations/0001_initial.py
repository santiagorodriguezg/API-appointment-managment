# Generated by Django 3.2.7 on 2021-09-16 14:15

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import encrypted_fields.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Room',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=60, unique=True, verbose_name='nombre')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='fecha de registro')),
                ('user_owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_owner', to=settings.AUTH_USER_MODEL, verbose_name='usuario que crea el chat')),
                ('user_receiver', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_receiver', to=settings.AUTH_USER_MODEL, verbose_name='usuario con quien comparte el chat')),
            ],
            options={
                'verbose_name': 'chat',
                'verbose_name_plural': 'chats',
                'db_table': 'room',
                'permissions': [('add_room_from_me', 'Can add my rooms'), ('change_room_from_me', 'Can change my rooms'), ('delete_room_from_me', 'Can delete my rooms'), ('view_room_from_me', 'Can view my rooms')],
            },
        ),
        migrations.CreateModel(
            name='Message',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.CharField(choices=[('AD', 'Audio'), ('FL', 'Archivo'), ('IMG', 'Imagen'), ('TXT', 'Texto'), ('VD', 'Video')], default='TXT', max_length=4, verbose_name='tipo de mensaje')),
                ('_content_data', encrypted_fields.fields.EncryptedTextField(default='')),
                ('content', encrypted_fields.fields.SearchField(blank=True, db_index=True, encrypted_field_name='_content_data', hash_key='60763429ba2a5bf74b7f94fb4db97c42ad37b0af59af5e8c5bb6592f1ecd752d', max_length=66, null=True, verbose_name='contenido')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='fecha de registro')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='fecha de actualización')),
                ('room', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='chats.room', verbose_name='chat')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='usuario')),
            ],
            options={
                'verbose_name': 'mensaje',
                'verbose_name_plural': 'mensajes',
                'db_table': 'message',
                'permissions': [('add_message_from_me', 'Can add my messages'), ('change_message_from_me', 'Can change my messages'), ('delete_message_from_me', 'Can delete my messages'), ('view_message_from_me', 'Can view my messages')],
            },
        ),
    ]
