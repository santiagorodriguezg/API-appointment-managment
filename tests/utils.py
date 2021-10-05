"""Testing utilities"""

import glob
import os
from datetime import timedelta

from rest_framework_simplejwt.tokens import Token

API_VERSION_V1 = 'v1'
API_ENDPOINT_V1 = f'api/{API_VERSION_V1}'
TEST_PASSWORD = 'sr123456'
TEST_IMG_FILE_NAME = 'IMG_test'
TEST_PDF_FILE_NAME = 'PDF_test'
TEST_AUDIO_FILE_NAME = 'audio_test'


class RefreshTokenTest(Token):
    """Refresh token test"""
    token_type = 'refresh'
    lifetime = timedelta(days=1)


class AccessTokenTest(Token):
    """Access token test"""
    token_type = 'access'
    lifetime = timedelta(days=1)


def delete_test_audio_files():
    """Deletes audio files used in tests"""
    for filename in glob.glob(f'media/appointments/audio/{TEST_AUDIO_FILE_NAME}*'):
        os.remove(filename)


def delete_test_img_files():
    """Deletes image files used in tests"""
    for filename in glob.glob(f'media/appointments/files/{TEST_IMG_FILE_NAME}*'):
        os.remove(filename)


def delete_test_pdf_files():
    """Deletes PDF files used in tests"""
    for filename in glob.glob(f'media/appointments/files/{TEST_PDF_FILE_NAME}*'):
        os.remove(filename)


def delete_all_test_files():
    """
    Delete all files used in tests.
    Call to delete_test_audio_files, delete_test_img_files, delete_test_pdf_files functions.
    """
    delete_test_audio_files()
    delete_test_img_files()
    delete_test_pdf_files()
