from django.utils import timezone
from django.shortcuts import render,get_object_or_404
from django.db.models import Q, Count
from rest_framework import generics, permissions, viewsets, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from firebase_auth.authentication import FirebaseAuthentication

from .models import (UserProfileModel,
                     UserFollowerModel,
                     User, 
                    #  UserNotifications,
                     UserBlockModel)
from .serializer import (UserModelSerializer,
                         FollowerSerializer, 
                         UserDetailSnippetSerializer, 
                        #  UserNotificationsSerializer, 
                         BlockSerializer)

from posts.models import Like,PostModel
from posts.serializers import PostModelSerializer
from posts.pagintation import TenPagintation, FivePagintation

from movieApp.models import MovieTestingModel

# from fcm_django.models import FCMDevice

# from .notifications import send_follow_notification
from .helpers import upload_to_b2, delete_from_b2
from django.core.cache import cache

# Create your views here.
class UserFeedView(APIView):
    pagintation_class = FivePagintation
    def get(self, request, format=None):
        following_ids = UserFollowerModel.objects.filter(follower=request.user).values_list('following', flat=True)
        liked_post_ids = Like.objects.filter(user=request.user).values_list('post__id',flat=True)
        user_liked_movies = MovieTestingModel.objects.filter(postmodel__like__user = request.user)

        timeline_posts = PostModel.objects.filter(
            Q(user__username__in = following_ids) | 
            Q(id__in=liked_post_ids) |
            Q(movie__in = user_liked_movies)
        ).exclude(
            id__in = liked_post_ids
        ).annotate(num_likes = Count('like'),num_comments = Count('comment'))

        for p in timeline_posts:
            time_since_posted = (timezone.now() - p.posted_at).total_seconds()/3600
            p.score = (p.num_likes*200) + (p.num_comments*30) - time_since_posted
        
        pagintator = self.pagintation_class()
        timeline_posts = sorted(timeline_posts, key=lambda p: p.score, reverse=True)
        paginatated_queryset = pagintator.paginate_queryset(timeline_posts, request)

        serializer = PostModelSerializer(paginatated_queryset, many=True, context={'request': request})

        return pagintator.get_paginated_response(serializer.data)

class UserProfileView(generics.RetrieveUpdateAPIView):
    authentication_classes = (FirebaseAuthentication,)
    # permission_classes = (IsAuthenticated)
    serializer_class = UserModelSerializer

    def get_object(self):
        return UserProfileModel.objects.get(user=self.request.user)

    def perform_update(self, serializer):
        if serializer.is_valid():
            instance = serializer.save()

        file_data = self.request.FILES.get('image')
        
        if file_data:
            if instance.profile_pic:
                delete_from_b2(instance.profile_pic)
            file_url = upload_to_b2(file_data=file_data, file_name=file_data.name)
            photo_url = f"https://reservoir-b.s3.us-east-005.backblazeb2.com/dp/{file_data.name}"

            instance.profile_pic = photo_url
            instance.save()

class UserDetailView(generics.RetrieveAPIView):
    queryset = UserProfileModel.objects.all()
    authentication_classes = (FirebaseAuthentication,)
    serializer_class = UserModelSerializer

class UserSnippetView(generics.RetrieveAPIView):
    queryset = UserProfileModel.objects.all()
    authentication_classes = (FirebaseAuthentication,)
    serializer_class = UserDetailSnippetSerializer


    # def get_queryset(self):
    #     return UserProfileModel.objects.filter(user=self.request.user)

    # def partial_update(self, request, *args, **kwargs):
    #     instance = self.get_object()
    #     serializer = self.get_serializer(instance,data=request.data, partial=True)
    #     serializer.is_valid(raise_exception=True)
    #     self.perform_update(serializer)
    #     return Response({'success':'User updated successfully'}, status=status.HTTP_200_OK)
   
    # def partial_update(self, request, *args, **kwargs):
    #     instance = self.get_object()
    #     serializer = self.get_serializer(instance, data=request.data, partial=True)
    #     serializer.is_valid(raise_exception=True)
    #     self.perform_update(serializer)
    #     return Response(serializer.data)
    
    # def perform_update(self, serializer):
    #     return serializer.save()
class FollowUser(generics.ListCreateAPIView):
    serializer_class = FollowerSerializer
    model = UserFollowerModel
    def get_queryset(self):
        return UserFollowerModel.objects.filter(follower=self.request.user)

    def perform_create(self, serializer):
        try:
            serializer.save(follower=self.request.user)
            # send_follow_notification(follower=self.request.user, followed=self.request.POST.get("following"))
            return Response(status=status.HTTP_201_CREATED)

            
        except:
            return Response(status=status.HTTP_400_BAD_REQUEST)

class UnfollowUser(generics.RetrieveDestroyAPIView):
    serializer_class = FollowerSerializer
    model = UserFollowerModel
    lookup_field = 'following'
    def get_queryset(self):
        return UserFollowerModel.objects.filter(follower=self.request.user)

class BlockUser(generics.ListCreateAPIView):
    serializer_class = BlockSerializer
    model = UserBlockModel
    pagination_class = TenPagintation
    def get_queryset(self):
        return UserBlockModel.objects.filter(blocker=self.request.user)

    def perform_create(self, serializer):
        try:
            curr_user = self.request.user
            serializer.save(blocker=curr_user)
            print(self.request.data.get('blocked'))
            cache_key = f"blocker_{curr_user}"
            cached_ids = cache.get(cache_key)
            print(f"cache ids before {cached_ids}")
            if cached_ids is not None:
            # Remove the user's ID from the cached set
                cached_ids.add(self.request.data.get('blocked'))
                
                # Update the cache with the modified set
                cache.set(cache_key, cached_ids)
            print(f"cache ids after {cached_ids}")

            return Response(status=status.HTTP_201_CREATED)
        except:
            return Response(status=status.HTTP_400_BAD_REQUEST)

class UnblockUser(generics.RetrieveDestroyAPIView):
    serializer_class = BlockSerializer
    # queryset = UserBlockModel.objects.all()
    lookup_field = 'blocked'

    def get_queryset(self):
        return UserBlockModel.objects.filter(blocker=self.request.user)
    
    def perform_destroy(self, instance):
        blocked = instance.blocked
        print(f"deleted user id {blocked}")
        instance.delete()
        cache_key = f"blocker_{self.request.user}"
        cached_ids = cache.get(cache_key)

        print(f"cache ids before {cached_ids}")
        if cached_ids is not None:
        # Remove the user's ID from the cached set
            cached_ids.remove(str(blocked))
            
            # Update the cache with the modified set
            cache.set(cache_key, cached_ids)
        print(f"cache ids after {cached_ids}")

        return Response(status=status.HTTP_204_NO_CONTENT)



# class FollowUser(APIView):
#     serializer_class = FollowerSerializer
#     def post(self,request):
#         pk = request.query_params.get('user')
#         follower = request.user
#         following = get_object_or_404(User,username=pk)
        
#         if follower == following:
#             return Response({'detail':'Can\'t follow yourself.'},status=status.HTTP_400_BAD_REQUEST)
        
#         follow = FollowUser.objects.filter(follower=follower,following=following)

#         if follow.exists():
#             return Response(status=status.HTTP_304_NOT_MODIFIED)
#         else:
#             follow = FollowUser(follower=follower,following=following)
#             serializer = FollowerSerializer(follow,data=request.data)
#             if serializer.is_valid():
#                 serializer.save()
#                 return Response(serializer.data,status=status.HTTP_201_CREATED)
#             else:
#                 return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)

#     def delete(self,request):
#         pk = request.query_params.get('user')
#         follower = request.user
#         following = get_object_or_404(User,username=pk)
#         follow = FollowUser.objects.filter(follower=follower,following=following)
#         if follow.exists():
#             follow.delete()
#             return Response(status=status.HTTP_204_NO_CONTENT)
#         else:
#             return Response(status=status.HTTP_304_NOT_MODIFIED)

# class RegisterDevice(generics.CreateAPIView):
#     queryset = FCMDevice.objects.all()

#     def perform_create(self, serializer):
#         user = UserProfileModel.objects.get(user=self.request.user)
#         serializer.save(user=user)

# class UnregisterDevice(generics.DestroyAPIView):
#     queryset = FCMDevice.objects.all()

#     def get_object(self):
#         user = UserProfileModel.objects.get(user=self.request.user)
#         return user.fcm_device

# @api_view(['POST'])
# def register_device(request):
#     user = request.user
#     registration_id = request.data.get('registration_id')
#     if user.is_authenticated and registration_id:
#         device, created = FCMDevice.objects.get_or_create(user=user, registration_id=registration_id)
#         if not created:
#             device.is_active = True
#             device.save()
#         return Response({'detail': 'Device registered.'})
#     return Response(status=400)


# @api_view(['DELETE'])
# def unregister_device(request):
#     user = request.user
#     registration_id = request.data.get('registration_id')
#     if user.is_authenticated and registration_id:
#         FCMDevice.objects.filter(user=user, registration_id=registration_id).delete()
#         return Response({'detail': 'Device unregistered.'})
#     return Response(status=400)

# class NotificationsViewset(generics.ListAPIView):
#     serializer_class = UserNotificationsSerializer
#     model = UserNotifications
#     pagination_class = TenPagintation
#     def get_queryset(self):
#         queryset = UserNotifications.objects.filter(user=self.request.user).order_by('-timestamp')
#         return queryset