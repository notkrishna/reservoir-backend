from django.shortcuts import render
from django.db.models import F
from rest_framework.response import Response
from rest_framework import viewsets, filters, generics,status
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from django.db import IntegrityError 
from firebase_auth.authentication import FirebaseAuthentication
from .models import (
    # MovieModel, 
    # ProgressMovies,
    # SavedMovies,
    # MovieList, 
    # FollowMovies, 
    RoleTestingModel,
    MovieTestingModel,
    CastTestingModel,
    SavedMoviesModel,
    ProgressMoviesModel,
    MovieListModel,
    FollowMoviesModel,
)
from .serializers import (
    MovieModelSerializer, 
    MovieSearchSerializer, 
    ProgressMovieSerializer, 
    SavedMovieSerializer, 
    MovieSnippetSerializer, 
    MovieListSerializer, 
    IsMovieInList,
    FollowMovieSerializer,
    RoleTestSerializer,
    MovieTestSerializer
    )

from posts.pagintation import FivePagintation, TenPagintation
from rest_framework.pagination import PageNumberPagination
from posts.mixins import CachedIdsMixin
from posts.permissions import OwnerPermission

from django.views.decorators.cache import cache_page
from rest_framework.decorators import action
# Create your views here.

class MovieModelViewSet(generics.RetrieveAPIView):
    authentication_classes = (FirebaseAuthentication,)
    queryset = MovieTestingModel.objects.all()
    serializer_class = MovieModelSerializer
    lookup_field = 'id'

    # @action(detail=True, methods=['get'])
    # @cache_page(60*60)
    def retrieve_movie(self, request, *args, **kwargs):
        movie = self.get_object()
        serializer = self.get_serializer(movie)
        return Response(serializer.data)

# class MovieCoverUpdateView(APIView):
#     def put(self, request, pk):
#         has_cover = MovieTestingModel.objects.get(id=pk)
#         serializer = MovieModelSerializer(has_cover, data=request.data, partial=True, context={'request': request})
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data)
#         return Response(serializer.errors, status=400)

# class MovieDetailViewset(generics.RetrieveAPIView):
#     def get_queryset(self):
#         movie = self.request.
#         return 

class MovieNameViewSet(APIView):
    def get(self,request,movie_id):
        try:
            movie = MovieTestingModel.objects.get(id=movie_id)
            data = {
                'name':movie.name,
            }
            return Response(data, status=status.HTTP_200_OK)
        except MovieTestingModel.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

class MovieSnippetViewset(generics.RetrieveAPIView):
    serializer_class = MovieSnippetSerializer
    queryset = MovieTestingModel.objects.all()

class MovieSearchAPIView(generics.ListAPIView):
    permission_classes = (AllowAny,)    
    search_fields = ["movie_name"]
    filter_backends = (filters.SearchFilter,)
    serializer_class = MovieSearchSerializer
    pagination_class = TenPagintation

    def get_queryset(self):
        if self.request.query_params.get('search'):    
            return MovieTestingModel.objects.all()
        return MovieTestingModel.objects.none()

class SavedMovieLists(generics.ListCreateAPIView):
    queryset = SavedMoviesModel.objects.all()
    serializer_class = SavedMovieSerializer
    authentication_classes = (FirebaseAuthentication,)
    pagination_class = TenPagintation
    # @action(detail=True, methods=['get'])
    # @cache_page(60*60)
    def get_queryset(self):
        queryset = SavedMoviesModel.objects.filter(user=self.request.user)
        movie = self.request.query_params.get('mn',None)
        if movie:
            queryset = queryset.objects.filter(movie_name=movie, user=self.request.user)
        return queryset

    # def perform_create(self, serializer):
    #     response = requests.get('http://192.168.1.9:8000/saved/')
    #     data = response.json()
    #     validated_data = SavedMovieSerializer(data)
    #     return serializer.save(user=self.request.user,**validated_data.data)

class SavedMovieCreate(generics.CreateAPIView):
    permission_classes = [OwnerPermission]
    queryset = SavedMoviesModel.objects.all()
    serializer_class = SavedMovieSerializer
    def perform_create(self, serializer):
        return serializer.save(user=self.request.user)

class SavedMovieDelete(generics.RetrieveDestroyAPIView):
    # queryset = SavedMovies.objects.all()
    serializer_class = SavedMovieSerializer
    lookup_field = 'movie_name'
    
    def get_queryset(self):
        return SavedMoviesModel.objects.filter(user=self.request.user)
    
class FollowMovieLists(generics.ListCreateAPIView):
    queryset = FollowMoviesModel.objects.all()
    serializer_class = FollowMovieSerializer
    authentication_classes = (FirebaseAuthentication,)

    def get_queryset(self):
        # queryset = FollowMoviesModel.objects.filter(user=self.request.user)
        movie = self.request.query_params.get('mn',None)
        if movie:
            queryset = FollowMoviesModel.objects.filter(movie_name=movie, user=self.request.user)
        return queryset

    # def perform_create(self, serializer):
    #     response = requests.get('http://192.168.1.9:8000/saved/')
    #     data = response.json()
    #     validated_data = SavedMovieSerializer(data)
    #     return serializer.save(user=self.request.user,**validated_data.data)

class FollowMovieCreate(generics.CreateAPIView):
    queryset = FollowMoviesModel.objects.all()
    serializer_class = FollowMovieSerializer
    def perform_create(self, serializer):
        return serializer.save(user=self.request.user)

class FollowMovieDelete(generics.RetrieveDestroyAPIView):
    # queryset = FollowMovies.objects.all()
    serializer_class = FollowMovieSerializer
    lookup_field = 'movie_name'
    
    def get_queryset(self):
        return FollowMoviesModel.objects.filter(user=self.request.user)


class ProgressWatchedMovieLists(CachedIdsMixin,generics.ListCreateAPIView):
    queryset = ProgressMoviesModel.objects.all()
    serializer_class = ProgressMovieSerializer
    authentication_classes = (FirebaseAuthentication,)
    pagination_class = FivePagintation

    def get_queryset(self):
        cached_ids = self.get_cached_ids()
        user = self.request.query_params.get('user',None)
        if user:
            queryset = ProgressMoviesModel.objects.filter(user=user).exclude(isDone=False)
        else:
            queryset = ProgressMoviesModel.objects.filter(user=self.request.user)
        movie = self.request.query_params.get('mn',None)
        if movie:
            queryset = queryset.filter(movie=movie)
        return queryset.exclude(user__in=cached_ids)

class ProgressMovieLists(CachedIdsMixin, generics.ListCreateAPIView):
    queryset = ProgressMoviesModel.objects.all()
    serializer_class = ProgressMovieSerializer
    authentication_classes = (FirebaseAuthentication,)
    pagination_class = FivePagintation

    def get_queryset(self):
        cached_ids = self.get_cached_ids()
        user = self.request.query_params.get('user')
        
        queryset = ProgressMoviesModel.objects.filter(user=user).exclude(isDone=True)
        movie = self.request.query_params.get('mn',None)
        if movie:
            queryset = ProgressMoviesModel.objects.filter(movie=movie)
        return queryset.exclude(user__in=cached_ids)

# class ProgressMovieDetailList(generics.ListCreateAPIView):
#     queryset = ProgressMovies.objects.all()
#     serializer_class = ProgressMovieDetailSerializer
#     authentication_classes = (FirebaseAuthentication,)
#     pagination_class = TenPagintation

#     def get_queryset(self):
#         movie = self.request.query_params.get('movie')
#         user = self.request.user        


# class ProgressMovieDone(generics.UAPIView):
#     queryset = ProgressMovies.objects.all()
#     serializer_class = ProgressMovieSerializer
#     def perform_create(self, serializer):
#         return serializer.save(user=self.request.user)

class ProgressMovieCreate(generics.CreateAPIView):
    queryset = ProgressMoviesModel.objects.all()
    serializer_class = ProgressMovieSerializer
    def perform_create(self, serializer):
        return serializer.save(user=self.request.user)

class ProgressMovieDelete(generics.RetrieveUpdateDestroyAPIView):
    queryset = ProgressMoviesModel.objects.all()
    serializer_class = ProgressMovieSerializer
    authentication_classes = (FirebaseAuthentication,)
    lookup_field = 'movie'

    def get_queryset(self):
        return ProgressMoviesModel.objects.filter(user=self.request.user)

class MovieListView(CachedIdsMixin, generics.ListAPIView):
    queryset = MovieListModel.objects.all()
    serializer_class = MovieListSerializer
    authentication_classes = (FirebaseAuthentication,)
    pagination_class = FivePagintation

    def get_queryset(self):
        cached_ids = self.get_cached_ids()

        user = self.request.query_params.get('user')
        queryset = MovieListModel.objects.filter(user=user).exclude(user__in=cached_ids)
        return queryset
    
class MovieListDetailView(CachedIdsMixin, APIView):
    serializer_class = MovieListSerializer
    # permission_classes
    def get(self,request, format=None):
        user = request.user
        movie = request.query_params.get('m')
        id = request.query_params.get('ls_id')
        try:

            obj = MovieListModel.objects.filter(id=id,movie=movie)
            serializer = MovieListSerializer(obj)
            if obj:
                return Response(serializer.data,status=status.HTTP_200_OK)
            else:
                return Response(status=status.HTTP_404_NOT_FOUND)
        except MovieListModel.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        except:
            return Response(status=status.HTTP_400_BAD_REQUEST)
    
    
    def post(self, request, format=None):
        action = request.query_params.get('action')
        movie_id = request.data.get('movie')
        list_id = request.data.get('id')

        if action == 'create':
            # Create a new movie list
            movie_list_name = request.data.get('list_name')

            try:
                movie_list = MovieListModel.objects.create(list_name=movie_list_name, user=request.user)
                serializer = MovieListSerializer(movie_list)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            except Exception as e:
                return Response({'message': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        elif action == 'add':
            try:
                movie = MovieTestingModel.objects.get(id=movie_id)
                movie_list = MovieListModel.objects.get(id=list_id)

                # Add the movie to the movie list
                movie_list.movie.add(movie)

                return Response({'message': 'Movie added to movie list.'}, status=status.HTTP_201_CREATED)

            except MovieTestingModel.DoesNotExist:
                return Response({'message': 'Invalid movie ID.'}, status=status.HTTP_400_BAD_REQUEST)
            except MovieListModel.DoesNotExist:
                return Response({'message': 'Invalid movie list ID.'}, status=status.HTTP_400_BAD_REQUEST)
            except Exception as e:
                return Response({'message': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        else:
            return Response({'message': 'Invalid action.'}, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request):
        action = request.query_params.get('action')
        movie_id = request.query_params.get('movie')
        list_id = request.query_params.get('id')

        if action == 'delete':
            # Delete a movie list
            # movie_list_name = request.data.get('list_name')

            try:
                movie_list = MovieListModel.objects.get(id=list_id, user=request.user)
                movie_list.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            except Exception as e:
                return Response({'message': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        elif action == 'remove':
            try:
                movie = MovieTestingModel.objects.get(id=movie_id)
                movie_list = MovieListModel.objects.get(id=list_id, user=request.user)

                # Add the movie to the movie list
                movie_list.movie.remove(movie)

                return Response(status=status.HTTP_204_NO_CONTENT)

            except MovieTestingModel.DoesNotExist:
                return Response({'message': 'Invalid movie ID.'}, status=status.HTTP_400_BAD_REQUEST)
            except MovieListModel.DoesNotExist:
                return Response({'message': 'Invalid movie list ID.'}, status=status.HTTP_400_BAD_REQUEST)
            except Exception as e:
                return Response({'message': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        else:
            return Response({'message': 'Invalid action.'}, status=status.HTTP_400_BAD_REQUEST)
        
    def put(self, request):
        list_id = request.query_params.get('id')

        try:
            ls = MovieListModel.objects.get(id=list_id)
        except Exception as e:
            return Response({'message': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        serializer = MovieListSerializer(ls, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data,status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)


class MovieListCheckView(generics.ListAPIView):
    queryset = MovieListModel.objects.all()
    serializer_class = MovieListSerializer
    authentication_classes = (FirebaseAuthentication,)
    pagination_class = TenPagintation

    def get_serializer_context(self):
        movie = self.request.query_params.get('m')
        context = super().get_serializer_context()
        context['movie_id'] = movie
        return context

    def get_queryset(self):
        ls = MovieListModel.objects.filter(user=self.request.user)
        return ls
    
class MovieListContentView(CachedIdsMixin, generics.ListAPIView):
    queryset = MovieListModel.objects.all()
    serializer_class = IsMovieInList
    pagination_class = TenPagintation

    def list(self, request, *args, **kwargs):
        cached_ids = self.get_cached_ids()

        list_id = self.request.query_params.get('list_id')
        movie_list = MovieListModel.objects.filter(id=list_id)
        movie_list = movie_list.first()
        print(movie_list.user)
        print(movie_list.user in cached_ids)

        if str(movie_list.user) in cached_ids:
            return Response(status=status.HTTP_403_FORBIDDEN)

        if movie_list is None:
            return self.get_paginated_response([])

        movie_ids = movie_list.movie.all().values('id','coverImgUrl','movie_name')
        pagintated_movie_ids = self.paginate_queryset(movie_ids)
        serializer = self.get_serializer(pagintated_movie_ids, many=True)
        
        return self.get_paginated_response(serializer.data)

class MovieButtonStates(APIView):
    def get(self,request,form=None):
        movie = request.query_params.get('movie')
        user = request.user
        saved = SavedMoviesModel.objects.filter(movie_name=movie, user=user).exists()
        progress = ProgressMoviesModel.objects.filter(movie_id=movie, user=user).exists()
        follow = FollowMoviesModel.objects.filter(movie_name=movie, user=user).exists()
        data = {
            'saved':saved,
            'progress':progress,
            'follow':follow
        }
        return Response(data)


# class MovieSearchAPIView(generics.ListCreateAPIView):
#     permission_classes = (AllowAny,)
#     search_fields = ['movie_name']
#     filter_backends = [filters.SearchFilter]
#     serializer_class = MovieModelSerializer
#     def get_queryset(self):
#         if self.request.query_params:
#             return MovieModel.objects.all()
#         return MovieModel.objects.none()


class MovieTestView(generics.ListAPIView):
    queryset = RoleTestingModel.objects.all()
    serializer_class = RoleTestSerializer
    def get_queryset(self):
        movie = self.request.query_params.get('movie')
        return RoleTestingModel.objects.filter(movie=movie)

class TestCast(generics.ListAPIView):
    queryset = MovieTestingModel.objects.all()
    serializer_class = MovieTestSerializer
    def get_queryset(self):
        cast = self.request.query_params.get('cast')
        return MovieTestingModel.objects.filter(movie__actor=cast)
















# class MovieModelViewSet(generics.RetrieveAPIView):
#     queryset = MovieModel.objects.all()
#     serializer_class = MovieModelSerializer
#     lookup_field = 'id'


# # class MovieDetailViewset(generics.RetrieveAPIView):
# #     def get_queryset(self):
# #         movie = self.request.
# #         return 

# class MovieNameViewSet(APIView):
#     def get(self,request,movie_id):
#         try:
#             movie = MovieModel.objects.get(id=movie_id)
#             data = {
#                 'name':movie.name,
#             }
#             return Response(data, status=status.HTTP_200_OK)
#         except MovieModel.DoesNotExist:
#             return Response(status=status.HTTP_404_NOT_FOUND)

# class MovieSnippetViewset(generics.RetrieveAPIView):
#     serializer_class = MovieSnippetSerializer
#     queryset = MovieModel.objects.all()

# class MovieSearchAPIView(generics.ListAPIView):
#     permission_classes = (AllowAny,)    
#     search_fields = ["movie_name","genres__name"]
#     filter_backends = (filters.SearchFilter,)
#     serializer_class = MovieSearchSerializer

#     def get_queryset(self):
#         if self.request.query_params.get('search'):    
#             return MovieModel.objects.all()
#         return MovieModel.objects.none()

# class SavedMovieLists(generics.ListCreateAPIView):
#     queryset = SavedMovies.objects.all()
#     serializer_class = SavedMovieSerializer
#     authentication_classes = (FirebaseAuthentication,)

#     def get_queryset(self):
#         queryset = SavedMovies.objects.filter(user=self.request.user)
#         movie = self.request.query_params.get('mn',None)
#         if movie:
#             queryset = SavedMovies.objects.filter(movie_name=movie)
#         return queryset

#     # def perform_create(self, serializer):
#     #     response = requests.get('http://192.168.1.9:8000/saved/')
#     #     data = response.json()
#     #     validated_data = SavedMovieSerializer(data)
#     #     return serializer.save(user=self.request.user,**validated_data.data)

# class SavedMovieCreate(generics.CreateAPIView):
#     queryset = SavedMovies.objects.all()
#     serializer_class = SavedMovieSerializer
#     def perform_create(self, serializer):
#         return serializer.save(user=self.request.user)

# class SavedMovieDelete(generics.RetrieveDestroyAPIView):
#     # queryset = SavedMovies.objects.all()
#     serializer_class = SavedMovieSerializer
#     lookup_field = 'movie_name'
    
#     def get_queryset(self):
#         return SavedMovies.objects.filter(user=self.request.user)
    
# class FollowMovieLists(generics.ListCreateAPIView):
#     queryset = FollowMovies.objects.all()
#     serializer_class = FollowMovieSerializer
#     authentication_classes = (FirebaseAuthentication,)

#     def get_queryset(self):
#         queryset = FollowMovies.objects.filter(user=self.request.user)
#         movie = self.request.query_params.get('mn',None)
#         if movie:
#             queryset = FollowMovies.objects.filter(movie_name=movie)
#         return queryset

#     # def perform_create(self, serializer):
#     #     response = requests.get('http://192.168.1.9:8000/saved/')
#     #     data = response.json()
#     #     validated_data = SavedMovieSerializer(data)
#     #     return serializer.save(user=self.request.user,**validated_data.data)

# class FollowMovieCreate(generics.CreateAPIView):
#     queryset = FollowMovies.objects.all()
#     serializer_class = FollowMovieSerializer
#     def perform_create(self, serializer):
#         return serializer.save(user=self.request.user)

# class FollowMovieDelete(generics.RetrieveDestroyAPIView):
#     # queryset = FollowMovies.objects.all()
#     serializer_class = FollowMovieSerializer
#     lookup_field = 'movie_name'
    
#     def get_queryset(self):
#         return FollowMovies.objects.filter(user=self.request.user)


# class ProgressWatchedMovieLists(generics.ListCreateAPIView):
#     queryset = ProgressMovies.objects.all()
#     serializer_class = ProgressMovieSerializer
#     authentication_classes = (FirebaseAuthentication,)
#     pagination_class = FivePagintation

#     def get_queryset(self):
#         user = self.request.query_params.get('user',None)
#         if user:
#             queryset = ProgressMovies.objects.filter(user=user).exclude(isDone=False)
#         else:
#             queryset = ProgressMovies.objects.filter(user=self.request.user).exclude(isDone=False)
#         movie = self.request.query_params.get('mn',None)
#         if movie:
#             queryset = ProgressMovies.objects.filter(movie=movie)
#         return queryset

# class ProgressMovieLists(generics.ListCreateAPIView):
#     queryset = ProgressMovies.objects.all()
#     serializer_class = ProgressMovieSerializer
#     authentication_classes = (FirebaseAuthentication,)
#     pagination_class = FivePagintation

#     def get_queryset(self):
#         user = self.request.query_params.get('user')
        
#         queryset = ProgressMovies.objects.filter(user=user).exclude(isDone=True)
#         movie = self.request.query_params.get('mn',None)
#         if movie:
#             queryset = ProgressMovies.objects.filter(movie=movie)
#         return queryset

# # class ProgressMovieDetailList(generics.ListCreateAPIView):
# #     queryset = ProgressMovies.objects.all()
# #     serializer_class = ProgressMovieDetailSerializer
# #     authentication_classes = (FirebaseAuthentication,)
# #     pagination_class = TenPagintation

# #     def get_queryset(self):
# #         movie = self.request.query_params.get('movie')
# #         user = self.request.user        


# # class ProgressMovieDone(generics.UAPIView):
# #     queryset = ProgressMovies.objects.all()
# #     serializer_class = ProgressMovieSerializer
# #     def perform_create(self, serializer):
# #         return serializer.save(user=self.request.user)

# class ProgressMovieCreate(generics.CreateAPIView):
#     queryset = ProgressMovies.objects.all()
#     serializer_class = ProgressMovieSerializer
#     def perform_create(self, serializer):
#         return serializer.save(user=self.request.user)

# class ProgressMovieDelete(generics.RetrieveUpdateDestroyAPIView):
#     queryset = ProgressMovies.objects.all()
#     serializer_class = ProgressMovieSerializer
#     authentication_classes = (FirebaseAuthentication,)
#     lookup_field = 'movie'

#     def get_queryset(self):
#         return ProgressMovies.objects.filter(user=self.request.user)

# class MovieListView(generics.ListAPIView):
#     queryset = MovieList.objects.all()
#     serializer_class = MovieListSerializer
#     authentication_classes = (FirebaseAuthentication,)
#     pagination_class = FivePagintation

#     def get_queryset(self):
#         user = self.request.query_params.get('user')
#         queryset = MovieList.objects.filter(user=user)
#         return queryset
    
# class MovieListDetailView(APIView):
#     serializer_class = MovieListSerializer
#     def get(self,request, format=None):
#         user = request.user
#         movie = request.query_params.get('m')
#         id = request.query_params.get('ls_id')
#         try:
#             obj = MovieList.objects.filter(id=id,movie=movie)
#             serializer = MovieListSerializer(obj)
#             if obj:
#                 return Response(serializer.data,status=status.HTTP_200_OK)
#             else:
#                 return Response(status=status.HTTP_404_NOT_FOUND)
#         except MovieList.DoesNotExist:
#             return Response(status=status.HTTP_404_NOT_FOUND)
#         except:
#             return Response(status=status.HTTP_400_BAD_REQUEST)
    
    
#     def post(self, request, format=None):
#         action = request.query_params.get('action')
#         movie_id = request.data.get('movie')
#         list_id = request.data.get('id')

#         if action == 'create':
#             # Create a new movie list
#             movie_list_name = request.data.get('list_name')

#             try:
#                 movie_list = MovieList.objects.create(list_name=movie_list_name, user=request.user)
#                 serializer = MovieListSerializer(movie_list)
#                 return Response(serializer.data, status=status.HTTP_201_CREATED)
#             except Exception as e:
#                 return Response({'message': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#         elif action == 'add':
#             try:
#                 movie = MovieModel.objects.get(id=movie_id)
#                 movie_list = MovieList.objects.get(id=list_id)

#                 # Add the movie to the movie list
#                 movie_list.movie.add(movie)

#                 return Response({'message': 'Movie added to movie list.'}, status=status.HTTP_201_CREATED)

#             except MovieModel.DoesNotExist:
#                 return Response({'message': 'Invalid movie ID.'}, status=status.HTTP_400_BAD_REQUEST)
#             except MovieList.DoesNotExist:
#                 return Response({'message': 'Invalid movie list ID.'}, status=status.HTTP_400_BAD_REQUEST)
#             except Exception as e:
#                 return Response({'message': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#         else:
#             return Response({'message': 'Invalid action.'}, status=status.HTTP_400_BAD_REQUEST)
    
#     def delete(self, request):
#         action = request.query_params.get('action')
#         movie_id = request.query_params.get('movie')
#         list_id = request.query_params.get('id')

#         if action == 'delete':
#             # Delete a movie list
#             # movie_list_name = request.data.get('list_name')

#             try:
#                 movie_list = MovieList.objects.get(id=list_id, user=request.user)
#                 movie_list.delete()
#                 return Response(status=status.HTTP_204_NO_CONTENT)
#             except Exception as e:
#                 return Response({'message': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#         elif action == 'remove':
#             try:
#                 movie = MovieModel.objects.get(id=movie_id)
#                 movie_list = MovieList.objects.get(id=list_id, user=request.user)

#                 # Add the movie to the movie list
#                 movie_list.movie.remove(movie)

#                 return Response(status=status.HTTP_204_NO_CONTENT)

#             except MovieModel.DoesNotExist:
#                 return Response({'message': 'Invalid movie ID.'}, status=status.HTTP_400_BAD_REQUEST)
#             except MovieList.DoesNotExist:
#                 return Response({'message': 'Invalid movie list ID.'}, status=status.HTTP_400_BAD_REQUEST)
#             except Exception as e:
#                 return Response({'message': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#         else:
#             return Response({'message': 'Invalid action.'}, status=status.HTTP_400_BAD_REQUEST)
        
#     def put(self, request):
#         list_id = request.query_params.get('id')

#         try:
#             ls = MovieList.objects.get(id=list_id)
#         except Exception as e:
#             return Response({'message': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
#         serializer = MovieListSerializer(ls, data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data,status=status.HTTP_200_OK)
#         else:
#             return Response(status=status.HTTP_400_BAD_REQUEST)


# class MovieListCheckView(generics.ListAPIView):
#     queryset = MovieList.objects.all()
#     serializer_class = MovieListSerializer
#     authentication_classes = (FirebaseAuthentication,)
#     pagination_class = TenPagintation

#     def get_serializer_context(self):
#         movie = self.request.query_params.get('m')
#         context = super().get_serializer_context()
#         context['movie_id'] = movie
#         return context

#     def get_queryset(self):
#         ls = MovieList.objects.filter(user=self.request.user)
#         return ls
    
# class MovieListContentView(generics.ListAPIView):
#     queryset = MovieList.objects.all()
#     serializer_class = IsMovieInList
#     pagination_class = TenPagintation

#     def list(self, request, *args, **kwargs):
#         list_id = self.request.query_params.get('list_id')
#         movie_list = MovieList.objects.filter(id=list_id)
#         movie_list = movie_list.first()
#         if movie_list is None:
#             return self.get_paginated_response([])

#         movie_ids = movie_list.movie.all().values('id','coverImgUrl')
#         pagintated_movie_ids = self.paginate_queryset(movie_ids)
#         serializer = self.get_serializer(pagintated_movie_ids, many=True)
        
#         return self.get_paginated_response(serializer.data)

# class MovieButtonStates(APIView):
#     def get(self,request,form=None):
#         movie = request.query_params.get('movie')
#         user = request.user
#         saved = SavedMovies.objects.filter(movie_name=movie, user=user).exists()
#         progress = ProgressMovies.objects.filter(movie_id=movie, user=user).exists()
#         follow = FollowMovies.objects.filter(movie_name=movie, user=user).exists()
#         data = {
#             'saved':saved,
#             'progress':progress,
#             'follow':follow
#         }
#         return Response(data)


# # class MovieSearchAPIView(generics.ListCreateAPIView):
# #     permission_classes = (AllowAny,)
# #     search_fields = ['movie_name']
# #     filter_backends = [filters.SearchFilter]
# #     serializer_class = MovieModelSerializer
# #     def get_queryset(self):
# #         if self.request.query_params:
# #             return MovieModel.objects.all()
# #         return MovieModel.objects.none()


# class MovieTestView(generics.ListAPIView):
#     queryset = RoleTestingModel.objects.all()
#     serializer_class = RoleTestSerializer
#     def get_queryset(self):
#         movie = self.request.query_params.get('movie')
#         return RoleTestingModel.objects.filter(movie=movie)

# class TestCast(generics.ListAPIView):
#     queryset = MovieTestingModel.objects.all()
#     serializer_class = MovieTestSerializer
#     def get_queryset(self):
#         cast = self.request.query_params.get('cast')
#         return MovieTestingModel.objects.filter(movie__actor=cast)