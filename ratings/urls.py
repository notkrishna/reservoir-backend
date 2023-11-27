from django.urls import include, path
from rest_framework import routers
from .views import GetMovieRatingViewSet,CreateMovieRatingViewSet, ListMovieRatingViewSet, ListMovieRatingUserViewSet, RatingLikeView, RatingLikeCount, ListRatingCommentRetrieveUpdateDeleteViewSet, ListRatingCommentViewSet, CreateRatingCommentViewSet, RatingCommentCount

# router = routers.DefaultRouter()
# router.register(r'',TimeStampDetailView)

urlpatterns = [
    path('<uuid:movie>/',GetMovieRatingViewSet.as_view()),
    path('create/<uuid:movie_id>/', CreateMovieRatingViewSet.as_view()),
    path('list/<uuid:movie>', ListMovieRatingViewSet.as_view()),
    path('list/user/', ListMovieRatingUserViewSet.as_view()),
    path('like/', RatingLikeView.as_view()),
    path('like_count/', RatingLikeCount.as_view()),
    path('comment/list/',ListRatingCommentViewSet.as_view()),
    path('comment/create/',CreateRatingCommentViewSet.as_view()),
    path('comment/<uuid:pk>/',ListRatingCommentRetrieveUpdateDeleteViewSet.as_view()),
    path('comment/comment_count/', RatingCommentCount.as_view())
    # path('stamp/', GetTimeStampDetail.as_view()),
]