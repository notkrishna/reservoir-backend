from rest_framework.exceptions import APIException
from rest_framework import status
class NoAuthToken(APIException):
    status_code = status.HTTP_401_UNAUTHORIZED
    default_detail = "No authentication provided"
    default_code = "no_auth_token"

class InvalidAuthToken(APIException):
    status_code = status.HTTP_401_UNAUTHORIZED
    default_detail = "Invalid authentication provided"
    default_code = "invalid_auth_token"

class FirebaseError(APIException):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    default_detail = "User doesn't exist"
    default_code = "no_firebase_uid"


