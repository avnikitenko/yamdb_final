from rest_framework import status
from rest_framework.exceptions import APIException


class CodeAPIException(APIException):
    status_code = status.HTTP_405_METHOD_NOT_ALLOWED
    default_code = 'error'

    def __init__(self, detail, status_code=None):
        self.detail = detail
        if status_code is not None:
            self.status_code = status_code
