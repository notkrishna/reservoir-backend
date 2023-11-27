from http.client import NOT_FOUND
from django.http import Http404
from django.db import IntegrityError
from django.db.models import Count
from django.shortcuts import render

from posts.permissions import OwnerPermission
from .serializer import TimeStampSerializer, TimestampLikeSerializer, TimestampCommentSerializer, TimeStampProgressSerializer
from rest_framework import viewsets, generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Timestamp, TimestampLike, TimestampComment
from firebase_auth.authentication import FirebaseAuthentication

from posts.pagintation import TenPagintation
from posts.mixins import CachedIdsMixin

# Create your views here.
class TimeStampDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Timestamp.objects.all()
    serializer_class = TimeStampSerializer
    def get_object(self):
        movie = self.kwargs.get('movie')
        stamp = self.kwargs.get('stamp')
        try:
            if movie and stamp:
                obj = Timestamp.objects.get(user=self.request.user,movie=movie,stamp=stamp)
                return obj
            else:
                return Response({}, status=status.HTTP_400_BAD_REQUEST)
        except AttributeError:
            raise Response(status=status.HTTP_404_NOT_FOUND)
        except Timestamp.DoesNotExist:
            raise Http404('Doesnt exist')


class TimeStampListView(APIView):
    queryset = Timestamp.objects.all()
    serializer_class = TimeStampSerializer
    def get(self,request):
        movie = request.query_params.get('movie')
        obj = Timestamp.objects.filter(user = self.request.user)
        try:
            if movie:
                obj = Timestamp.objects.filter(movie=movie, user=request.user).order_by('stamp').values_list('stamp', flat=True)
                ls = list(obj)
                if ls:
                    return Response(ls)
                else:
                    return Response(status=status.HTTP_404_NOT_FOUND)
            else:
                return Response(status=status.HTTP_400_BAD_REQUEST)
        except AttributeError:
            raise Response(status=status.HTTP_404_NOT_FOUND)
    
    # def put(self):
    #     movie = self.kwargs.get('movie')
    #     stamp = self.kwargs.get('stamp')
    #     try:
    #         if movie and stamp:
    #             obj = Timestamp.objects.get(user=self.request.user,movie=movie,stamp=stamp)
    #             serializer = self.serializer_class(obj, data=self.request.data)
    #             if serializer.is_valid():
    #                 serializer.save()
    #                 return Response(serializer.data)
    #             else:
    #                 return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    #     except AttributeError:
    #         raise Response(status=status.HTTP_404_NOT_FOUND)

    # def delete(self):
    #     movie = self.kwargs.get('movie')
    #     stamp = self.kwargs.get('stamp')
    #     try:
    #         if movie and stamp:
    #             obj = Timestamp.objects.get(user=self.request.user,movie=movie,stamp=stamp)
    #             obj.delete()
    #             return Response(status=status.HTTP_204_NO_CONTENT)
    #     except AttributeError:
    #         raise Response(status=status.HTTP_404_NOT_FOUND)


class CurrGetTimeStampList(generics.ListCreateAPIView):
    serializer_class = TimeStampSerializer
    authentication_classes = (FirebaseAuthentication,)
    queryset = Timestamp.objects.all()
    pagination_class = TenPagintation

    def get_queryset(self):
        queryset = Timestamp.objects.filter(user=self.request.user).order_by('stamp')
        return queryset
    
    def perform_create(self, serializer):
        try:    
            serializer.save(user=self.request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except IntegrityError:
            return Response(status=status.HTTP_400_BAD_REQUEST)

class ListTimestampViewSet(CachedIdsMixin, generics.ListAPIView):
    # queryset = Timestamp.objects.all()
    serializer_class = TimeStampSerializer
    authentication_classes = (FirebaseAuthentication,)
    pagination_class = TenPagintation

    def get_queryset(self):
        cached_ids = self.get_cached_ids()
        print(cached_ids)
        print(self.request.user)
        try:
            movie = self.kwargs.get('movie')
            ls = Timestamp.objects.filter(movie=movie).exclude(user__in = cached_ids)
            
            return ls
        except AttributeError:
            return Response({'message':'Attribute error occured'},status=status.HTTP_400_BAD_REQUEST)
        except Timestamp.DoesNotExist:
            raise Http404
        except IntegrityError:
            return Response({'message':'Integrity error occured'}, status=status.HTTP_400_BAD_REQUEST)
        
class TimestampProgressDetailList(CachedIdsMixin, generics.ListCreateAPIView):
    queryset = Timestamp.objects.all()
    serializer_class = TimeStampProgressSerializer
    authentication_classes = (FirebaseAuthentication,)
    pagination_class = TenPagintation
    permission_classes = [OwnerPermission]

    def get_queryset(self):
        cached_ids = self.get_cached_ids()

        movie = self.request.query_params.get('movie')
        user = self.request.query_params.get('user')


        queryset = Timestamp.objects.filter(movie=movie,user=user).exclude(user__in=cached_ids).order_by('stamp')
        return queryset

        


class TimestampLikeView(CachedIdsMixin, APIView):
    serializer_class = TimestampLikeSerializer

    def get(self,request):
        user = request.user
        post_id = request.query_params.get('post_id')
        try:
            post = Timestamp.objects.get(id=post_id)
            # if not post:
            #     return Response(status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        
        try:
            like = TimestampLike.objects.get(user=user, post=post_id)
            serializer = TimestampLikeSerializer(like)
            return Response(serializer.data)
        except TimestampLike.DoesNotExist:
            return Response(data={"message":"Doesnt exist"},status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response(status=status.HTTP_400_BAD_REQUEST)

    def post(self,request):
        user = request.user
        serializer = TimestampLikeSerializer(data=request.data)

        serializer.is_valid()
        # post_data = serial
        cached_ids = self.get_cached_ids()
        # print(cached_ids)
        # print(serializer.validated_data['post'].user)

        post_author = serializer.validated_data['post'].user
        post_id = serializer.validated_data['post']

        if str(post_author) in cached_ids:
            # print("yep blocked")
            return Response(status=status.HTTP_403_FORBIDDEN)
        

        like = TimestampLike.objects.create(user=user, post=post_id)
        serializer = TimestampLikeSerializer(like)
    
        return Response(serializer.data, status=status.HTTP_201_CREATED)
        



        # user = request.user
        # post_id = request.data.get('post_id')
        # try:
        #     post = Timestamp.objects.get(id=post_id)
        #     # if not post:
        #     #     return Response(status=status.HTTP_400_BAD_REQUEST)
        # except:
        #     return Response(status=status.HTTP_400_BAD_REQUEST)
        
        # try:
        #     like = TimestampLike.objects.get(user=user, post=post_id)
        #     return Response(status=status.HTTP_400_BAD_REQUEST)

        # except TimestampLike.DoesNotExist:
        #     like = TimestampLike.objects.create(user=user, post=post)
        #     serializer = TimestampLikeSerializer(like)
        
        #     return Response(serializer.data, status=status.HTTP_201_CREATED)
        # except:
        #     return Response(status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self,request):
        user = request.user
        post_id = request.query_params.get('post_id')
        try:
            post = Timestamp.objects.get(id=post_id)
            # if not post:
            #     return Response(status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        
        try:
            like = TimestampLike.objects.get(user=user, post=post_id)
            like.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Timestamp.DoesNotExist:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response(status=status.HTTP_400_BAD_REQUEST)

class TimestampLikeCount(APIView):
    def get(self, request):
        post_id = request.query_params.get('post_id')
        count = TimestampLike.objects.filter(post=post_id).count()
        return Response({'like_count':count})
    


############

class CreateTimestampCommentViewSet(CachedIdsMixin, generics.CreateAPIView):
    queryset = TimestampComment.objects.all()
    serializer_class = TimestampCommentSerializer
    permission_classes = [OwnerPermission]
    def perform_create(self, serializer):
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

class ListTimestampCommentViewSet(CachedIdsMixin, generics.ListAPIView):
    queryset = TimestampComment.objects.all()
    serializer_class = TimestampCommentSerializer
    lookup_field = 'post'
    pagination_class = TenPagintation
    def get_queryset(self):
        user = self.request.user
        cached_ids = self.get_cached_ids()
        try:
            post = self.request.query_params.get('post')
            post_author = Timestamp.objects.get(id=post).user

            print(str(post_author) in cached_ids)

            if str(post_author) in cached_ids:
                print("yep blocked")
                return TimestampComment.objects.none()
            
            if post is not None:
                ls = TimestampComment.objects.filter(post=post)
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
        #         list = TimestampComment.objects.filter(post=post).annotate(comment_count=Count('id'))
        #         return list
        #     else:
        #         return Response(status=status.HTTP_400_BAD_REQUEST)
        except AttributeError:
            return Response({'message':'Attribute error occured'},status=status.HTTP_400_BAD_REQUEST)
        except Timestamp.DoesNotExist:
            return Response({'message':'Instance not found'}, status=status.HTTP_404_NOT_FOUND)
        except IntegrityError:
            return Response({'message':'Integrity error occured'}, status=status.HTTP_400_BAD_REQUEST)

class ListUserTimestampCommentViewSet(generics.ListAPIView):
    queryset = TimestampComment.objects.all()
    serializer_class = TimestampCommentSerializer
    def get_queryset(self):
        user = self.request.user
        # posts = PostModel.objects.prefetch_related('likes')
        # posts = posts.annotate(likes_count = Count('likes'))
        # if user.is_authenticated:
        #     posts = posts.annotate(has_liked=Case(When(likes__user = user, then=True),default=False))
        # else:
        #     posts = posts.annotate(has_liked = False)
        try:
            list = TimestampComment.objects.filter(user=self.request.user)
            return list

        except AttributeError:
            return Response({'message':'Attribute error occured'},status=status.HTTP_400_BAD_REQUEST)
        except Timestamp.DoesNotExist:
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

class ListTimestampCommentRetrieveUpdateDeleteViewSet(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [OwnerPermission]
    authentication_classes = (FirebaseAuthentication,)
    queryset = TimestampComment.objects.all()
    serializer_class = TimestampCommentSerializer

class TimestampCommentCount(APIView):
    def get(self, request):
        post_id = request.query_params.get('post_id')
        count = TimestampComment.objects.filter(post=post_id).count()
        return Response({'comment_count':count})


    
