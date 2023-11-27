from rest_framework import serializers, exceptions
from .models import (UserProfileModel,
                     UserFollowerModel, 
                    #  UserNotifications,
                     UserBlockModel)
from ratings.models import MovieRatings
from django.db.models import Count, Avg
from decimal import Decimal, ROUND_UP

class UserModelSerializer(serializers.ModelSerializer):
    rating_count = serializers.SerializerMethodField(read_only=True)
    avg_rating = serializers.SerializerMethodField(read_only=True)
    follower_count = serializers.SerializerMethodField(read_only=True)
    class Meta:
        model = UserProfileModel
        fields = '__all__'
        read_only_fields = ['user']
    def get_avg_rating(self,obj):
        user = self.instance.user
        data = MovieRatings.objects.filter(user=user)
        if data:
            average_rating = data.aggregate(avg_rating = Avg('rating'))
            avg_rating = Decimal(average_rating['avg_rating']).quantize(Decimal('0.0'), rounding=ROUND_UP)
            return avg_rating
        else:
            return float(0)

    def get_rating_count(self,obj):
        user = self.instance.user
        data = MovieRatings.objects.filter(user=user)
        if data:
            no_of_ratings = MovieRatings.objects.filter(user=user).aggregate(rating_count = Count('id'))
            return no_of_ratings['rating_count']
        else:
            return int(0)

    def get_follower_count(self,obj):
        user = self.instance.user
        data = MovieRatings.objects.filter(user=user)
        if data:
            no_of_followers = UserFollowerModel.objects.filter(following=user).aggregate(follower_count = Count('id'))
            return no_of_followers['follower_count']
        else:
            return int(0)

class UserDetailSnippetSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfileModel
        fields = ['user','usertag','profile_pic']
        read_only_fields = ['user','usertag','profile_pic']

            
class FollowerSerializer(serializers.ModelSerializer):
#     followers_count = serializers.SerializerMethodField()
    # following_count = serializers.SerializerMethodField()
    class Meta:
        model = UserFollowerModel
        fields = ['follower','following','id']
        read_only_fields = ['follower']
    
class BlockSerializer(serializers.ModelSerializer):
    blockedUsertag = serializers.CharField(source = 'blocked.profile.usertag', read_only=True)
    class Meta:
        model = UserBlockModel
        fields = ['blocker','blocked','id','blockedUsertag']
        read_only_fields = ['id','blocker']
    # def get_followers_count(self,obj):
        # return obj.follower.count()
    # 
    # def get_following_count(self,obj):
        # return obj.following.count()
    

# class UserNotificationsSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = UserNotifications
#         fields = '__all__'
#         read_only_fields = ['title','body','timestamp']