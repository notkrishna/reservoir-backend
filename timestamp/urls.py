from django.urls import include, path
from rest_framework import routers
from .views import TimeStampDetailView,CurrGetTimeStampList,TimeStampListView, ListTimestampViewSet,TimestampLikeView, TimestampLikeCount, CreateTimestampCommentViewSet, ListTimestampCommentViewSet, ListTimestampCommentRetrieveUpdateDeleteViewSet, ListUserTimestampCommentViewSet, TimestampCommentCount, TimestampProgressDetailList

# router = routers.DefaultRouter()
# router.register(r'',TimeStampDetailView)

urlpatterns = [
    path('<uuid:movie>&<int:stamp>', TimeStampDetailView.as_view()),
    path('list/', CurrGetTimeStampList.as_view()),
    path('stampList/',TimeStampListView.as_view()),
    path('list/m/<uuid:movie>', ListTimestampViewSet.as_view()),
    path('list/progress/', TimestampProgressDetailList.as_view()),
    path('like/', TimestampLikeView.as_view()),
    path('like_count/',TimestampLikeCount.as_view()),
    path('comment/list/',ListTimestampCommentViewSet.as_view()),
    path('comment/create/',CreateTimestampCommentViewSet.as_view()),
    path('comment/<uuid:pk>/', ListTimestampCommentRetrieveUpdateDeleteViewSet.as_view()),
    path('comment/list/user/', ListUserTimestampCommentViewSet.as_view()),
    path('comment/comment_count/', TimestampCommentCount.as_view())
    # path('stamp/', GetTimeStampDetail.as_view()),
]