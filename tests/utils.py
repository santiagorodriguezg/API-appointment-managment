"""Testing utilities"""

from datetime import timedelta

from rest_framework_simplejwt.tokens import Token

TEST_PASSWORD = 'sr123456'
API_VERSION_V1 = 'v1'


class RefreshTokenTest(Token):
    """Refresh token test"""
    token_type = 'refresh'
    lifetime = timedelta(days=1)


class AccessTokenTest(Token):
    """Access token test"""
    token_type = 'access'
    lifetime = timedelta(days=1)
