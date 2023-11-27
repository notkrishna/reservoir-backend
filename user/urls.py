from django.contrib import admin
from django.urls import path, include
from .views import (UserProfileView,
                    FollowUser,
                    UnfollowUser,
                    UserDetailView,
                    UserSnippetView, 
                    UserFeedView, 
                    # register_device, 
                    # unregister_device, 
                    # NotificationsViewset,
                    BlockUser,
                    UnblockUser)
from rest_framework import routers
from . import views

# router = routers.DefaultRouter()
# router.register(r'',UserProfileView)

urlpatterns = [
    path('edit/', UserProfileView.as_view()),
    path('<str:pk>', UserDetailView.as_view()),
    path('follow/',FollowUser.as_view()),
    path('isfollowing/<str:following>',UnfollowUser.as_view()),
    path('block/',BlockUser.as_view()),
    path('block_more/<str:blocked>',UnblockUser.as_view()),
    path('snippet/<str:pk>/',UserSnippetView.as_view()),
    path('feed/', UserFeedView.as_view()),
    # path('register-device/', views.register_device),
    # path('unregister-device/', views.unregister_device),
    # path('notifications/', NotificationsViewset.as_view())
]

# urlpatterns = [
#     path('',UserProfileView.as_view())
# ]
