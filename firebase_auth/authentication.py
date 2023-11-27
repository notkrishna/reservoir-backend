import os
import firebase_admin
from rest_framework import authentication
from rest_framework import exceptions
from user.models import User, UserProfileModel
from django.utils import timezone
import requests

from firebase_admin import credentials
from firebase_admin import auth

from .exceptions import NoAuthToken
from .exceptions import InvalidAuthToken
from .exceptions import FirebaseError

from dotenv import load_dotenv

cred = credentials.Certificate({
  "type": os.getenv("type"),
  "project_id": os.getenv("project_id"),
  "private_key_id": ("private_key_id"),
  "private_key": os.getenv("private_key"),
  "client_email": os.getenv("client_email"),
  "client_id": os.getenv("client_id"),
  "auth_uri": os.getenv("auth_uri"),
  "token_uri": os.getenv("token_uri"),
  "auth_provider_x509_cert_url": os.getenv("auth_provider_x509_cert_url"),
  "client_x509_cert_url": os.getenv("client_x509_cert_url")
})

default = firebase_admin.initialize_app(cred)



class FirebaseAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        auth_header = request.META.get("HTTP_AUTHORIZATION", None)
        if not auth_header:
            raise NoAuthToken("No auth token found")
        
        id_token = auth_header.split(" ").pop()
        t = id_token
        decoded_token = None

        try:
            decoded_token = auth.verify_id_token(id_token)
        except Exception:
            raise InvalidAuthToken("Invalid token")
            pass

        if not id_token or not decoded_token:
            return None
        
        try:
            uid = decoded_token.get("uid")
        except Exception:
            raise FirebaseError()
        
        user, created = User.objects.get_or_create(username = uid)
        print(f"created? {created}")
        
        # try:
        # profile, created_profile = UserProfileModel.objects.get_or_create(user=uid,usertag = uid)
        try:
            profile = UserProfileModel.objects.get(user=uid)
            print(f"profile_created? {profile}")
        except UserProfileModel.DoesNotExist:
            UserProfileModel.objects.create(user=user, usertag=uid)
        except:
            pass
            

        return (user, None)


# from rest_framework import authentication
# from rest_framework import exceptions
# from firebase_admin import auth

# class FirebaseAuthentication(authentication.BaseAuthentication):
#     def authenticate(self, request):
#         auth_header = request.META.get('HTTP_AUTHORIZATION', None)
#         if not auth_header:
#             return None

#         parts = auth_header.split()

#         if parts[0].lower() != 'bearer':
#             raise exceptions.AuthenticationFailed('Invalid header format')
#         elif len(parts) == 1:
#             raise exceptions.AuthenticationFailed('Invalid header format')
#         elif len(parts) > 2:
#             raise exceptions.AuthenticationFailed('Invalid header format')

#         token = parts[1]
#         try:
#             decoded_token = auth.verify_id_token(token)
#         except Exception as e:
#             raise exceptions.AuthenticationFailed(str(e))

#         user_id = decoded_token.get('uid')
#         if not user_id:
#             raise exceptions.AuthenticationFailed('Token does not contain user id')

#         try:
#             user = User.objects.get(id=user_id)
#         except User.DoesNotExist:
#             raise exceptions.AuthenticationFailed('User not found')

#         return (user, token)

