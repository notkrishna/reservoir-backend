import io
import os
import tempfile
from django.shortcuts import render
from django.db.models import Count,Case,When
from django.conf import settings
from django.core.files.storage import default_storage
from django.db import IntegrityError
from django.db.models import Q

from rest_framework import viewsets, generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticatedOrReadOnly, BasePermission
from rest_framework.pagination import PageNumberPagination

from posts.permissions import OwnerPermission, IsBlockedOrBlocker, HideBlockedContentPermission
from .mixins import CachedIdsMixin, WriteCachedIdsMixin

from user.models import UserBlockModel

from firebase_auth.authentication import FirebaseAuthentication
from .models import PostModel,Like, Comment
from .serializers import PostModelSerializer, LikeSerializer, CommentSerializer
from .pagintation import TenPagintation, FivePagintation
from .helpers import delete_from_b2

from b2sdk.v1 import B2Api

import redis

from django.core.cache import cache

# class OwnerPermission(BasePermission):
#     def has_object_permission(self, request, view, obj):
#         if request.method in ['GET','HEAD','OPTIONS']:
#             return True
#         return obj.user == request.user

# Create your views here.

class CreatePostViewSet(generics.CreateAPIView):
    queryset = PostModel.objects.all()
    serializer_class = PostModelSerializer
    authentication_classes = (FirebaseAuthentication,)
    # permission_classes = [IsBlockedOrBlocker]
    def perform_create(self, serializer):
        try:
            post_type = self.request.data.get('post_type')
            file_data = self.request.FILES.get('image')
            movie = self.request.data.get('movie')
            print(movie)

            if post_type == 'photo' and file_data:
                # Upload the image file to Backblaze B2
                
                b2_api = B2Api()
                # b2_api.authorize_account('production', settings.B2_ACCOUNT_ID, settings.B2_APPLICATION_KEY)
                b2_api.authorize_account('production', settings.B2_ACCOUNT_ID, settings.B2_APPLICATION_KEY)

                bucket = b2_api.get_bucket_by_name(settings.B2_BUCKET_NAME)
                # file_data = self.request.data['image']
                file_name = os.path.basename(file_data.name)
                folder_name = 'post_imgs'
                file_path = os.path.join(folder_name,file_name)
                file_data.seek(0)

                # file_size = file_data.size
                
                # with tempfile.NamedTemporaryFile() as temp_file:
                #     # Write the image data to the temporary file
                #     temp_file.write(file_data.read())

                uploaded_file = bucket.upload_bytes(file_data.read(),file_name = file_path)

                # Save the post with the photo URL
                photo_url = f"https://reservoir-b.s3.us-east-005.backblazeb2.com/post_imgs/{file_name}"
                
                serializer.is_valid()
                movie_post = serializer.save(user=self.request.user, photo_url=photo_url)

                post_cache_key = f"movie_posts:{movie}"
                post_cache = cache.get(post_cache_key)
                print(post_cache)
                if post_cache:
                    post_cache.append(movie_post)
                    cache.set(post_cache_key, post_cache)
                    print(post_cache)


            else:
                serializer.is_valid()
                
                movie_post = serializer.save(user=self.request.user, photo_url=None)
                print(movie_post)

                post_cache_key = f"movie_posts:{movie}"
                post_cache = cache.get(post_cache_key)
                print(post_cache)
                if post_cache:
                    post_cache.append(movie_post)
                    cache.set(post_cache_key, post_cache)
                    print(post_cache)

        except IntegrityError:
            return Response({'message':'Attribute error occured'}, status=status.HTTP_400_BAD_REQUEST)

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        return Response(response.data,status=status.HTTP_201_CREATED)



# class ListPostViewSet(generics.ListAPIView):
#     serializer_class = PostModelSerializer
#     pagination_class = FivePagintation
#     permission_classes = [IsBlockedOrBlocker]
#     def get_serializer_context(self):
#         context = super().get_serializer_context()
#         context['request'] = self.request
#         return context

#     def get_queryset(self):
#         queryset = PostModel.objects.all()
#         # queryset = queryset.filter(movie=movie).select_related('user__blocked_users', 'user__blocked_by_users').exclude(
#         #     Q(user__in=blocked_users) | Q(user__in=blocked_by_users)
#         # )
#         user = self.request.user

#         blocked_users = UserBlockModel.objects.filter(blocker=user).values_list('blocked', flat=True)
#         blocked_by_user = UserBlockModel.objects.filter(blocked=user).values_list('blocker', flat=True)
#         # posts = PostModel.objects.prefetch_related('likes')
#         # posts = posts.annotate(likes_count = Count('likes'))
#         # if user.is_authenticated:
#         #     posts = posts.annotate(has_liked=Case(When(likes__user = user, then=True),default=False))
#         # else:
#         #     posts = posts.annotate(has_liked = False)

#         try:
#             movie = self.kwargs.get('movie')
#             if movie is not None:
#                 ls = queryset.filter(movie=movie).prefetch_related('user__blocked_users', 'user__blocked_by_users').exclude(
#                     Q(user__username__in=blocked_users) | Q(user__username__in=blocked_by_user)
#                 )
#                 # ls = queryset.filter(movie=movie).exclude(user__in=blocked_users)
#                 # ls = ls.exclude(user__in=blocked_by_user)
#                 return ls
#             else:
#                 return Response(status=status.HTTP_400_BAD_REQUEST)
#         except AttributeError:
#             return Response({'message':'Attribute error occured'},status=status.HTTP_400_BAD_REQUEST)
#         except PostModel.DoesNotExist:
#             return Response({'message':'Instance not found'}, status=status.HTTP_404_NOT_FOUND)
#         except IntegrityError:
#             return Response({'message':'Integrity error occured'}, status=status.HTTP_400_BAD_REQUEST)



class ListPostViewSet(CachedIdsMixin, generics.ListAPIView):
    serializer_class = PostModelSerializer
    pagination_class = FivePagintation
    # permission_classes = [IsBlockedOrBlocker]
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

    def get_queryset(self):
        # queryset = PostModel.objects.all()
        # queryset = queryset.filter(movie=movie).select_related('user__blocked_users', 'user__blocked_by_users').exclude(
        #     Q(user__in=blocked_users) | Q(user__in=blocked_by_users)
        # )

        # blocked = UserBlockModel.objects.filter(Q(blocker=user) | Q(blocked=user))

        # blocked_users = UserBlockModel.objects.filter(blocker=user).values_list('blocked', flat=True)
        # blocked_by_user = UserBlockModel.objects.filter(blocked=user).values_list('blocker', flat=True)
        
        # posts = PostModel.objects.prefetch_related('likes')
        # posts = posts.annotate(likes_count = Count('likes'))
        # if user.is_authenticated:
        #     posts = posts.annotate(has_liked=Case(When(likes__user = user, then=True),default=False))
        # else:
        #     posts = posts.annotate(has_liked = False)

        
        
        # try:
        #     movie = self.kwargs.get('movie')
        #     ls = queryset.filter(movie=movie).prefetch_related('user__blocked', 'user__blocked').exclude(
        #         Q(user__username__in=blocked_users) | Q(user__username__in=blocked_by_user)
        #     )
        #         # ls = queryset.filter(movie=movie).exclude(user__in=blocked_users)
        #         # ls = ls.exclude(user__in=blocked_by_user)
        #     return ls

        user = self.request.user
        cached_ids = self.get_cached_ids()
        print(cached_ids)
        print(self.request.user)
        try:
            movie = self.kwargs.get('movie')
            post_cache_key = f"movie_posts:{movie}"
            queryset = cache.get(post_cache_key)
            cache.delete(queryset)
            print("what")
            print(f"cache {queryset}")
            if queryset:
                print(f"From cache {queryset}")
                return queryset
            else:
                queryset = list(PostModel.objects.filter(movie=movie).exclude(user__in = cached_ids))
                cache.set(post_cache_key, queryset, 60*5)
            return queryset

        except AttributeError:
            return Response({'message':'Attribute error occured'},status=status.HTTP_400_BAD_REQUEST)
        except PostModel.DoesNotExist:
            return Response({'message':'Instance not found'}, status=status.HTTP_404_NOT_FOUND)
        except IntegrityError:
            return Response({'message':'Integrity error occured'}, status=status.HTTP_400_BAD_REQUEST)


class ListUserPostViewSet(CachedIdsMixin, generics.ListAPIView):
    queryset = PostModel.objects.all()
    serializer_class = PostModelSerializer
    pagination_class = FivePagintation
    def get_queryset(self):
        param = self.request.query_params.get('u')
        try:
            if param:
                curr_user = self.request.user
                cached_ids = self.get_cached_ids()
                ls = PostModel.objects.filter(user=param).exclude(user__in = cached_ids)
            elif param is None:
                ls = PostModel.objects.filter(user=curr_user).exclude(user__in = cached_ids)
            return ls
        except AttributeError:
            return Response({'message':'Attribute error occured'},status=status.HTTP_400_BAD_REQUEST)
        except PostModel.DoesNotExist:
            return Response({'message':'Instance not found'}, status=status.HTTP_404_NOT_FOUND)
        except IntegrityError:
            return Response({'message':'Integrity error occured'}, status=status.HTTP_400_BAD_REQUEST)
        

class ListRetrieveUpdateDeleteViewSet(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [OwnerPermission]
    authentication_classes = (FirebaseAuthentication,)
    queryset = PostModel.objects.all()
    serializer_class = PostModelSerializer
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        post_type = instance.post_type
        if post_type=='photo':
            delete_from_b2(instance.photo_url)
            self.perform_destroy(instance)
            return Response(status=status.HTTP_204_NO_CONTENT)

        else:
            self.perform_destroy(instance)
            return Response(status=status.HTTP_204_NO_CONTENT)

class LikeView(CachedIdsMixin, APIView):
    serializer_class = LikeSerializer

    def get(self,request):
        user = request.user
        post_id = request.query_params.get('post_id')
        try:
            post = PostModel.objects.get(id=post_id)
            # if not post:
            #     return Response(status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        
        try:
            like = Like.objects.get(user=user, post=post_id)
            serializer = LikeSerializer(like)
            return Response(serializer.data)
        except Like.DoesNotExist:
            return Response(data={"message":"Doesnt exist"},status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response(status=status.HTTP_400_BAD_REQUEST)

    def post(self,request):
        user = request.user
        serializer = LikeSerializer(data=request.data)

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
        

        like = Like.objects.create(user=user, post=post_id)
        serializer = LikeSerializer(like)
    
        return Response(serializer.data, status=status.HTTP_201_CREATED)
        

        # try:
        #     post = PostModel.objects.get(id=post_id)
        #     # if not post:
        #     #     return Response(status=status.HTTP_400_BAD_REQUEST)
        # except:
        #     return Response(status=status.HTTP_400_BAD_REQUEST)
        
        # try:
        #     like = Like.objects.get(user=user, post=post_id)
        #     return Response(status=status.HTTP_400_BAD_REQUEST)

        # try:
        
        
        # except:
        #     return Response(status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self,request):
        user = request.user
        post_id = request.query_params.get('post_id')
        try:
            post = PostModel.objects.get(id=post_id)
            # if not post:
            #     return Response(status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        
        try:
            like = Like.objects.get(user=user, post=post_id)
            like.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Like.DoesNotExist:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response(status=status.HTTP_400_BAD_REQUEST)

class PostLikeCount(CachedIdsMixin, APIView):
    def get(self, request):
        serializer = LikeSerializer(data=request.data)
        post_id = request.data.get('post')
        print(serializer)
        serializer.is_valid()

        post_id = request.query_params.get('post_id')
        cache_ids = self.get_cached_ids()
        # if 
        count = Like.objects.filter(post=post_id).count()
        return Response({'like_count':count})

###################
# from .signals import send_comment_notification
class CreatePostCommentViewSet(CachedIdsMixin, APIView):
    permission_classes = [OwnerPermission]
    def post(self, request):
        user = request.user
        # post_data = request.data.get('post')s
        serializer = CommentSerializer(data=request.data)
        serializer.is_valid()
        # post_data = serial
        cached_ids = self.get_cached_ids()
        print(cached_ids)
        print(serializer.validated_data['post'].user,serializer)

        post_author = serializer.validated_data['post'].user

        if str(post_author) in cached_ids:
            print("yep blocked")
            return Response(status=status.HTTP_403_FORBIDDEN)
        
        if serializer.is_valid():
            serializer.save(user=request.user)
            # send_comment_notification.delay()

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(status=status.HTTP_400_BAD_REQUEST)

# class CreatePostCommentViewSet(generics.CreateAPIView):
#     queryset = Comment.objects.all()
#     serializer_class = CommentSerializer
#     def perform_create(self, serializer):
#         try:
#             curr_user = self.request.user
#             if serializer.is_valid():
#                 serializer.save(user=curr_user)
#             else:
#                 return Response({'message':'Invalid request'}, status=status.HTTP_400_BAD_REQUEST)

#         except IntegrityError:
#             return Response({'message':'Attribute error occured'}, status=status.HTTP_400_BAD_REQUEST)
    
#     def post(self, request, *args, **kwargs):
#         response = super().post(request, *args, **kwargs)
#         return Response(response.data,status=status.HTTP_201_CREATED)

class ListPostCommentViewSet(CachedIdsMixin, generics.ListAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    lookup_field = 'post'
    pagination_class = TenPagintation
    def get_queryset(self):
        user = self.request.user
        # serializer = CommentSerializer
        # posts = PostModel.objects.prefetch_related('likes')
        # posts = posts.annotate(likes_count = Count('likes'))
        # if user.is_authenticated:
        #     posts = posts.annotate(has_liked=Case(When(likes__user = user, then=True),default=False))
        # else:
        #     posts = posts.annotate(has_liked = False)
        cached_ids = self.get_cached_ids()
        try:
            post = self.request.query_params.get('post')
            post_author = PostModel.objects.get(id=post).user

            print(str(post_author) in cached_ids)

            if str(post_author) in cached_ids:
                print("yep blocked")
                return Comment.objects.none()
            
            if post is not None:
                ls = Comment.objects.filter(post=post)
                return ls
            else:
                return Response(status=status.HTTP_400_BAD_REQUEST)

            # if ls
            # .order_by('-created_at')
            
            
        except AttributeError:
            return Response({'message':'Attribute error occured'},status=status.HTTP_400_BAD_REQUEST)
        except PostModel.DoesNotExist:
            return Response({'message':'Instance not found'}, status=status.HTTP_404_NOT_FOUND)
        except IntegrityError:
            return Response({'message':'Integrity error occured'}, status=status.HTTP_400_BAD_REQUEST)

class ListUserPostCommentViewSet(generics.ListAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    def get_queryset(self):
        user = self.request.user
        # posts = PostModel.objects.prefetch_related('likes')
        # posts = posts.annotate(likes_count = Count('likes'))
        # if user.is_authenticated:
        #     posts = posts.annotate(has_liked=Case(When(likes__user = user, then=True),default=False))
        # else:
        #     posts = posts.annotate(has_liked = False)
        try:
            list = Comment.objects.filter(user=self.request.user)
            return list

        except AttributeError:
            return Response({'message':'Attribute error occured'},status=status.HTTP_400_BAD_REQUEST)
        except PostModel.DoesNotExist:
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

class ListCommentRetrieveUpdateDeleteViewSet(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [OwnerPermission]
    authentication_classes = (FirebaseAuthentication,)
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer

class CommentCount(APIView):
    def get(self, request):
        post_id = request.query_params.get('post_id')
        count = Comment.objects.filter(post=post_id).count()
        return Response({'comment_count':count})

# class LikeView(generics.CreateAPIView):
#     queryset = Like.objects.all()
#     serializer_class = LikeSerializer
#     def perform_create(self, serializer):
#         return serializer.save(user=self.request.user)

# class UnlikeView(generics.RetrieveDestroyAPIView):
#     # queryset = PostModel.objects.all()
#     serializer_class = LikeSerializer
#     lookup_field = 'post'
    
#     def get_queryset(self):
#         return Like.objects.all()


# class LikeViewset(APIView):
#     def put(self,request,post_id):
#         user = request.user

#         try:
#             post = PostModel.objects.get(id=post_id)
#         except PostModel.DoesNotExist:
#             return Response(status=status.HTTP_404_NOT_FOUND)

#         if user in post.likes.all():
#             post.likes.remove(user)
#             return Response(status=status.HTTP_204_NO_CONTENT)
#         else:
#             post.likes.add(user)
#             return Response(status=status.HTTP_201_CREATED)