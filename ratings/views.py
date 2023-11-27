from django.http import Http404
from django.shortcuts import render
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework import viewsets, status, generics
from rest_framework.views import APIView
from django.db import IntegrityError
from django.db.models import F

from posts.permissions import OwnerPermission
from movieApp.models import MovieTestingModel
from user.models import UserProfileModel

from posts.pagintation import TenPagintation
from posts.mixins import CachedIdsMixin

from firebase_auth.authentication import FirebaseAuthentication
from .models import MovieRatings, RatingLike, RatingComment
from .serializers import MovieRatingsSerializer, RatingLikeSerializer, RatingCommentSerializer
from .pagintation import MovieRatingPagination

# Create your views here.
class MovieRatingViewset(viewsets.ModelViewSet):
    queryset = MovieRatings.objects.all()
    serializer_class = MovieRatingsSerializer
    
class GetMovieRatingViewSet(generics.RetrieveUpdateDestroyAPIView):
    queryset = MovieRatings.objects.all()
    serializer_class = MovieRatingsSerializer
    def get_object(self):
        try:
            movie = self.kwargs.get('movie')
            obj = MovieRatings.objects.get(movie=movie,user=self.request.user)
            return obj
        except AttributeError:
            return Response({'message':'Attribute error occured'},status=status.HTTP_400_BAD_REQUEST)
        except MovieRatings.DoesNotExist:
            raise Http404
        except IntegrityError:
            return Response({'message':'Integrity error occured'}, status=status.HTTP_400_BAD_REQUEST)

# class CreateMovieRatingViewSet(generics.CreateAPIView):
#     queryset = MovieRatings.objects.all()
#     serializer_class = MovieRatingsSerializer
#     authentication_classes = (FirebaseAuthentication,)

#     def perform_create(self, serializer):
#         m = self.kwargs.get('movie')
#         try:
#             if m is not None:
#                return serializer.save(user=self.request.user, movie = m)
#         except IntegrityError:
#             return Response({'message':'Attribute error occured'}, status=status.HTTP_400_BAD_REQUEST)

class CreateMovieRatingViewSet(APIView):
    def post(self,request,movie_id):
        movie = get_object_or_404(MovieTestingModel, id=movie_id)
        serializer = MovieRatingsSerializer(data=request.data, context={'request':request})
        if serializer.is_valid():
            rating = serializer.validated_data['rating']
            review = serializer.validated_data['review']
            user = request.user
            serializer.save(movie=movie,user=user,rating=rating,review=review)
            # movie_rating = MovieRatings.objects.create(movie=movie,user=user,rating=rating,review=review)
            return Response(serializer.data,status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=400)

class ListMovieRatingViewSet(CachedIdsMixin, generics.ListAPIView):
    queryset = MovieRatings.objects.all()
    serializer_class = MovieRatingsSerializer
    authentication_classes = (FirebaseAuthentication,)
    pagination_class = MovieRatingPagination

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

    def list(self,request, *args, **kwargs):
        try:
            movie = self.kwargs.get('movie')
            cached_ids = self.get_cached_ids()
            print(cached_ids)
            print(self.request.user)
            
            if movie is not None:
                queryset = MovieRatings.objects.filter(movie=movie).exclude(user__in = cached_ids)
                is_reviewed = queryset.filter(user=self.request.user).exists()

                pagination_class = self.pagination_class()
                paginated_queryset = pagination_class.paginate_queryset(queryset,request)
                
                #Provides context to the serializer for isLiked field
                serializer_context = {
                    'request':request
                }
                
                serializer = self.serializer_class(paginated_queryset, many=True, context = serializer_context)

                pagination_class.is_reviewed = is_reviewed


                return pagination_class.get_paginated_response(serializer.data)
            else:
                return Response(status=status.HTTP_400_BAD_REQUEST)
        except AttributeError:
            return Response({'message':'Attribute error occured'},status=status.HTTP_400_BAD_REQUEST)
        except MovieRatings.DoesNotExist:
            raise Http404
        except IntegrityError:
            return Response({'message':'Integrity error occured'}, status=status.HTTP_400_BAD_REQUEST)

class ListMovieRatingUserViewSet(CachedIdsMixin, generics.ListAPIView):
    queryset = MovieRatings.objects.all()
    serializer_class = MovieRatingsSerializer
    authentication_classes = (FirebaseAuthentication,)
    pagination_class = TenPagintation

    def get_queryset(self):
        cached_ids = self.get_cached_ids()
        user = self.request.query_params.get('user')
        try:
            list = MovieRatings.objects.filter(user=user).exclude(user__in=cached_ids)
            return list
           
        except AttributeError:
            return Response({'message':'Attribute error occured'},status=status.HTTP_400_BAD_REQUEST)
        except MovieRatings.DoesNotExist:
            raise Http404
        except IntegrityError:
            return Response({'message':'Integrity error occured'}, status=status.HTTP_400_BAD_REQUEST)
            
class RatingLikeView(CachedIdsMixin, APIView):
    serializer_class = RatingLikeSerializer

    def get(self,request):
        user = request.user
        rating_id = request.query_params.get('post_id')
        try:
            rating = MovieRatings.objects.get(id=rating_id)
            # if not post:
            #     return Response(status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        
        try:
            like = RatingLike.objects.get(user=user, post=rating_id)
            serializer = RatingLikeSerializer(like)
            return Response(serializer.data)
        except RatingLike.DoesNotExist:
            return Response(data={"message":"Doesnt exist"},status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response(status=status.HTTP_400_BAD_REQUEST)

    def post(self,request):
        user = request.user
        serializer = RatingLikeSerializer(data=request.data)

        serializer.is_valid()
        # post_data = serial
        cached_ids = self.get_cached_ids()
        print(cached_ids)
        print(serializer.validated_data['post'].user)

        post_author = serializer.validated_data['post'].user
        post_id = serializer.validated_data['post']

        if str(post_author) in cached_ids:
            print("yep blocked")
            return Response(status=status.HTTP_403_FORBIDDEN)
        

        like = RatingLike.objects.create(user=user, post=post_id)
        serializer = RatingLikeSerializer(like)
    
        return Response(serializer.data, status=status.HTTP_201_CREATED)
        

        # user = request.user
        # rating_id = request.data.get('post_id')
        # try:
        #     rating = MovieRatings.objects.get(id=rating_id)
        #     # if not post:
        #     #     return Response(status=status.HTTP_400_BAD_REQUEST)
        # except:
        #     return Response(status=status.HTTP_400_BAD_REQUEST)
        
        # try:
        #     like = RatingLike.objects.get(user=user, post=rating_id)
        #     return Response(status=status.HTTP_400_BAD_REQUEST)

        # except RatingLike.DoesNotExist:
        #     like = RatingLike.objects.create(user=user, post=rating)
        #     serializer = RatingLikeSerializer(like)
        
        #     return Response(serializer.data, status=status.HTTP_201_CREATED)
        # except:
        #     return Response(status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self,request):
        user = request.user
        rating_id = request.query_params.get('post_id')
        try:
            rating = MovieRatings.objects.get(id=rating_id)
            # if not post:
            #     return Response(status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        
        try:
            like = RatingLike.objects.get(user=user, post=rating_id)
            like.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except RatingLike.DoesNotExist:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response(status=status.HTTP_400_BAD_REQUEST)


class RatingLikeCount(APIView):
    def get(self, request):
        rating_id = request.query_params.get('rating_id')
        count = RatingLike.objects.filter(post=rating_id).count()
        return Response({'like_count':count})

###################

class CreateRatingCommentViewSet(CachedIdsMixin, APIView):
    # queryset = RatingComment.objects.all()
    # serializer_class = RatingCommentSerializer
    def post(self, request):
        serializer = RatingCommentSerializer(data=request.data)
        try:
            serializer.is_valid()
        # post_data = serial
            cached_ids = self.get_cached_ids()
            print(cached_ids)
            print(serializer.validated_data['post'].user)

            post_author = serializer.validated_data['post'].user

            if str(post_author) in cached_ids:
                print("yep blocked")
                return Response(status=status.HTTP_403_FORBIDDEN)
            
            if serializer.is_valid():
                serializer.save(user=self.request.user)
                return Response(status=status.HTTP_201_CREATED)
            return Response({'message':'Invalid request'}, status=status.HTTP_400_BAD_REQUEST)

        except IntegrityError:
            return Response({'message':'Attribute error occured'}, status=status.HTTP_400_BAD_REQUEST)

        
        # try:
        #     if serializer.is_valid():
        #         serializer.save(user=self.request.user)
        #         return Response(serializer.data,status=status.HTTP_201_CREATED)
        #     else:
        #         return Response({'message':'Invalid request'}, status=status.HTTP_400_BAD_REQUEST)

        # except IntegrityError:
        #     return Response({'message':'Attribute error occured'}, status=status.HTTP_400_BAD_REQUEST)

class ListRatingCommentViewSet(CachedIdsMixin, generics.ListAPIView):
    queryset = RatingComment.objects.all()
    serializer_class = RatingCommentSerializer
    pagination_class = TenPagintation
    def get_queryset(self):
        user = self.request.user
        cached_ids = self.get_cached_ids()
        try:
            post = self.request.query_params.get('post')
            print(post)
            post_author = MovieRatings.objects.get(id=post).user

            print(str(post_author) in cached_ids)

            if str(post_author) in cached_ids:
                print("yep blocked")
                return RatingComment.objects.none()
            
            if post is not None:
                ls = RatingComment.objects.filter(post=post)
                return ls
            else:
                return Response(status=status.HTTP_400_BAD_REQUEST)

        # # posts = PostModel.objects.prefetch_related('likes')
        # # posts = posts.annotate(likes_count = Count('likes'))
        # # if user.is_authenticated:
        # #     posts = posts.annotate(has_liked=Case(When(likes__user = user, then=True),default=False))
        # # else:
        # #     posts = posts.annotate(has_liked = False)
        # try:
        #     post = self.request.query_params.get('post')
        #     if post is not None:
        #         list = RatingComment.objects.filter(post=post)
        #         return list
        #     else:
        #         return Response(status=status.HTTP_400_BAD_REQUEST)
        except AttributeError:
            return Response({'message':'Attribute error occured'},status=status.HTTP_400_BAD_REQUEST)
        except RatingComment.DoesNotExist:
            return Response({'message':'Instance not found'}, status=status.HTTP_404_NOT_FOUND)
        except IntegrityError:
            return Response({'message':'Integrity error occured'}, status=status.HTTP_400_BAD_REQUEST)

# class ListUserPosViewSet(generics.ListAPIView):
#     queryset = PostModel.objects.all()
#     serializer_class = PostModelSerializer
#     def get_queryset(self):
#         try:
#             list = PostModel.objects.filter(user=self.request.user)
#             return list
#         except AttributeError:
#             return Response({'message':'Attribute error occured'},status=status.HTTP_400_BAD_REQUEST)
#         except PostModel.DoesNotExist:
#             return Response({'message':'Instance not found'}, status=status.HTTP_404_NOT_FOUND)
#         except IntegrityError:
#             return Response({'message':'Integrity error occured'}, status=status.HTTP_400_BAD_REQUEST)

class ListRatingCommentRetrieveUpdateDeleteViewSet(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [OwnerPermission]
    authentication_classes = (FirebaseAuthentication,)
    queryset = RatingComment.objects.all()
    serializer_class = RatingCommentSerializer

class RatingCommentCount(APIView):
    def get(self, request):
        rating_id = request.query_params.get('rating_id')
        count = RatingComment.objects.filter(post=rating_id).count()
        return Response({'comment_count':count})

