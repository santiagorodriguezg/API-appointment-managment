"""Exceptions"""

from rest_framework import status
from rest_framework.exceptions import APIException


class BadRequest(APIException):
    """
    Incorrect requests or requests. Throws HTTP error code 400.
    Should be used when an error response is required.

    Example of the output format:

    .. code-block:: json

        {
            "errors": [
                "error detail"
            ]
        }
    """

    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Petición o Solicitud Incorrecta'
    default_code = 'bad_request'

    def __init__(self, detail=None):
        if detail is None:
            detail = self.default_detail

        self.detail = {'errors': [detail]}
