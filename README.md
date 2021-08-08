# Gestión de citas para la Fundación de la Mujer en Boyacá

API REST con Python y Django.

## Requerimientos

**Python 3.9**

**PostgreSQL 12, 13**

## Instalación

1. Instalar versión de python 3.9 de acuerdo a su sistema operativo.

   [Descargar Python](https://www.python.org/downloads/)


2. Instalar virtualenv para crear entornos virtuales de Python:

   ```bash
   pip install virtualenv
   ```

3. Clonar el proyecto.

4. Crear entorno virtual:

   ```bash
   virtualenv venv
   ```

5. Activar entorno virtual:

   ```bash
   cd venv/Scripts/activate
   ```

6. Instalar requerimientos:

   ```bash
   pip install -r requirements/local.txt
   ```

7. Configurar variables de entorno en el archivo `.env` (Ver el archivo `.env.example`).


8. Ejecutar migraciones:

   ```bash
   python manage.py migrate
   ```

9. Ejecutar el servidor local:

   ```bash
   python manage.py runserver
   ```

## Generar SECRET_KEY para Django Settings

Para generar una cadena aleatoria de 50 caracteres utilizable en el archivo `.env` como valor de ajuste
de `settings.SECRET_KEY` de Django ejecute el comando:

```bash
python manage.py shell -c 'from django.core.management import utils; print(utils.get_random_secret_key())'
```

## Generar llaves de encriptación (Mensajes chat)

Los mensajes en formato de texto enviados a través del chat son encriptados antes de guardarse en la base de datos. Se
utiliza el cifrado AES-256 con el modo GCM (a través de la
biblioteca [Pycryptodome](https://www.pycryptodome.org/en/latest/src/cipher/aes.html)).

Para generar la llave de encriptación utilizada como valor de ajuste de `settings.FIELD_ENCRYPTION_KEYS` ejecute en la
terminal el comando:

```bash
python manage.py shell
```

Luego:

```python
import secrets

secrets.token_hex(32)
```

Visitar el siguiente enlace
para [más información](https://gitlab.com/guywillett/django-searchable-encrypted-fields/-/tree/master#generating-encryption-keys)
.

## Generar constraseña para Redis

Es importante especificar un valor muy fuerte y largo como contraseña. En lugar de crear una contraseña puede usar el
siguiente comando para generar una aleatoria:

```bash
openssl rand 60 | openssl base64 -A
```

Visitar el siguiente enlace
para [más información](https://www.digitalocean.com/community/tutorials/how-to-install-and-secure-redis-on-ubuntu-20-04#step-4-%E2%80%94-configuring-a-redis-password)
.

## Tests

Se utiliza `pytest` como framework de prueba. Consultar la [documentación de pytest](https://pytest.org) para mas
opciones al ejecutar los tests.

Para ejecutar los tests use el siguiente comando:

```bash
pytest
```

## Configuración de correos electrónicos

1. Habilitar la opción `Acceso de aplicaciones poco seguras`.

2. Deshabilitar CAPTCHA para Gmail:

   [Deshabilitar CAPTCHA](https://www.google.com/accounts/UnlockCaptcha).

   Visitar el siguiente enlace para [más información](https://support.google.com/mail/?p=BadCredentials).

```
Gracias!.
```