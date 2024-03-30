from django.test import TestCase

# Create your tests here.
import pytest
from django.test import RequestFactory
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token
from .views import UserFeedView, UserProfileView, UserDetailView, UserSnippetView, FollowUser, UnfollowUser, BlockUser, UnblockUser

User = get_user_model()

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def user():
    return User.objects.create(username='testuser', email='test@reservoir.com')

@pytest.fixture
def token(user):
    return Token.objects.create(user=user)

def test_user_feed_view(api_client, user, token):
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
    response = api_client.get('/user/feed/')
    assert response.status_code == 200

def test_user_profile_view(api_client, user, token):
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
    response = api_client.get('/user/profile/')
    assert response.status_code == 200

def test_user_detail_view(api_client, user, token):
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
    response = api_client.get(f'/user/detail/{user.id}/')
    assert response.status_code == 200

def test_user_snippet_view(api_client, user, token):
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
    response = api_client.get('/user/snippet/')
    assert response.status_code == 200

def test_follow_user_view(api_client, user, token):
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
    response = api_client.post('/user/follow/', {'following': 1}, format='json')
    assert response.status_code == 201

def test_unfollow_user_view(api_client, user, token):
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
    response = api_client.delete('/user/unfollow/1/')
    assert response.status_code == 204

def test_block_user_view(api_client, user, token):
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
    response = api_client.post('/user/block/', {'blocked': 1}, format='json')
    assert response.status_code == 201

def test_unblock_user_view(api_client, user, token):
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
    response = api_client.delete('/user/unblock/1/')
    assert response.status_code == 204
