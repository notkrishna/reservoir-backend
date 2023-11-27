from django.urls import include, path
from rest_framework import routers
from .views import CreatePostViewSet, ListPostViewSet, ListUserPostViewSet, ListRetrieveUpdateDeleteViewSet, LikeView, PostLikeCount, ListCommentRetrieveUpdateDeleteViewSet, CreatePostCommentViewSet, ListPostCommentViewSet, ListUserPostCommentViewSet, CommentCount

urlpatterns = [
    path('create/',CreatePostViewSet.as_view()),
    path('list/<uuid:movie>',ListPostViewSet.as_view()),
    path('list/user/',ListUserPostViewSet.as_view()),
    path('<uuid:pk>/', ListRetrieveUpdateDeleteViewSet.as_view()),
    path('like/', LikeView.as_view()),
    path('like_count/', PostLikeCount.as_view()),
    path('comment/list/',ListPostCommentViewSet.as_view()),
    path('comment/create/',CreatePostCommentViewSet.as_view()),
    path('comment/<uuid:pk>/', ListCommentRetrieveUpdateDeleteViewSet.as_view()),
    path('comment/list/user/', ListUserPostCommentViewSet.as_view()),
    path('comment/comment_count/', CommentCount.as_view())
    # path('unlike/<int:post>/', UnlikeView.as_view()),
]
