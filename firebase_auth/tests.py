from django.test import TestCase

# Create your tests here.
import os
import pytest
from django.test import RequestFactory
from .authentication import FirebaseAuthentication
from .exceptions import NoAuthToken, InvalidAuthToken, FirebaseError
from user.models import User, UserProfileModel

@pytest.fixture
def firebase_auth():
    return FirebaseAuthentication()

@pytest.fixture
def valid_token():
    # Provide a valid Firebase ID token for testing
    return os.getenv("VALID_FIREBASE_ID_TOKEN")

@pytest.fixture
def invalid_token():
    # Provide an invalid Firebase ID token for testing
    return os.getenv("INVALID_FIREBASE_ID_TOKEN")

def test_valid_authentication(firebase_auth, valid_token):
    request = RequestFactory().get('/')
    request.META['HTTP_AUTHORIZATION'] = f'Bearer {valid_token}'
    
    user, _ = firebase_auth.authenticate(request)
    
    assert isinstance(user, User)

def test_invalid_authentication_missing_token(firebase_auth):
    request = RequestFactory().get('/')
    
    with pytest.raises(NoAuthToken):
        firebase_auth.authenticate(request)

def test_invalid_authentication_invalid_token(firebase_auth, invalid_token):
    request = RequestFactory().get('/')
    request.META['HTTP_AUTHORIZATION'] = f'Bearer {invalid_token}'
    
    with pytest.raises(InvalidAuthToken):
        firebase_auth.authenticate(request)

