from django.urls import include, path
from rest_framework import routers
from .views import (MovieModelViewSet, 
      MovieSnippetViewset, 
          MovieSearchAPIView, 
              SavedMovieLists, 
                  SavedMovieDelete, 
                      SavedMovieCreate, 
                        ProgressMovieCreate, 
                              ProgressMovieDelete, 
                                ProgressMovieLists, 
                                      MovieListView, 
                                        MovieListDetailView, 
                                        MovieListCheckView, 
                                        MovieListContentView,
                                        FollowMovieCreate,
                                        FollowMovieLists,
                                        FollowMovieDelete,
                                        MovieButtonStates,
                                        ProgressWatchedMovieLists,
                                        MovieTestView,
                                        TestCast,
                                        # MovieCoverUpdateView
                                        )
from movieApp import views

# router = routers.DefaultRouter()
# router.register(r'm',MovieModelViewSet)

urlpatterns = [
    path('m/<uuid:id>/', MovieModelViewSet.as_view()),
    # path('m/update/cover/<uuid:pk>/', MovieCoverUpdateView.as_view()),
    path('m/snippet/<uuid:pk>/', MovieSnippetViewset.as_view()),
    path('movieSearch/',views.MovieSearchAPIView.as_view()),
    path('saved/', SavedMovieLists.as_view()),
    path('saved/<uuid:movie_name>/',SavedMovieDelete.as_view()),
    path('saved/create/',SavedMovieCreate.as_view()),
    path('m/follow/', FollowMovieLists.as_view()),
    path('m/follow/<uuid:movie_name>/',FollowMovieDelete.as_view()),
    path('m/follow/create/',FollowMovieCreate.as_view()),
    path('progress/', ProgressMovieLists.as_view()),
    path('progress/watched/', ProgressWatchedMovieLists.as_view()),
    path('progress/<uuid:movie>/', ProgressMovieDelete.as_view()),
    path('progress/create/', ProgressMovieCreate.as_view()),
    path('mls/',MovieListView.as_view()),
    path('mls/d/',MovieListDetailView.as_view()),
    path('mls/check/', MovieListCheckView.as_view()),
    path('mls/content/',MovieListContentView.as_view()),
    path('m/mbtnstates/',MovieButtonStates.as_view()),
    path('m/test/', MovieTestView.as_view()),
    path('m/test/cast/', TestCast.as_view())
]
