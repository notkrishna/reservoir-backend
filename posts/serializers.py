from rest_framework import serializers
from .models import PostModel, Like, Comment

from datetime import datetime
from django.utils.timesince import timesince
from django.utils.timezone import make_aware

from user.models import UserBlockModel

class HumanReadableDateTimeField(serializers.DateTimeField):
    def to_representation(self, value):
        now = make_aware(datetime.now())
        difference = now - value

        if difference.days > 365:
            # If the time difference is greater than 1 year, display in years
            years = difference.days // 365
            return f"{years}y ago"

        if difference.days > 30:
            # If the time difference is greater than 1 month, display in months
            months = difference.days // 30
            return f"{months}m ago"

        if difference.days > 0:
            # If the time difference is greater than 1 day, display in days
            return f"{difference.days}d ago"

        return timesince(value, now).split(",")[0] + " ago"

class PostModelSerializer(serializers.ModelSerializer):
    usertag = serializers.CharField(source='user.profile.usertag', read_only=True)
    profile_pic = serializers.CharField(source='user.profile.profile_pic', read_only=True)
    posted_at = HumanReadableDateTimeField(read_only=True)
    like_count = serializers.SerializerMethodField(read_only=True)
    is_liked = serializers.SerializerMethodField(read_only=True)
    comment_count = serializers.SerializerMethodField(read_only=True)
    class Meta:
        model = PostModel
        fields = '__all__'
        read_only_fields = ['user','usertag','posted_at']
    def get_like_count(self,obj):
        return Like.objects.filter(post=obj).count()
    def get_is_liked(self,obj):
        curr_user = self.context['request'].user
        return Like.objects.filter(post=obj,user=curr_user).exists()
    def get_comment_count(self,obj):
        return Comment.objects.filter(post=obj).count()
# class PhotoSerializer(PostModelSerializer):
#     class Meta(PostModelSerializer.Meta):
#         model = Photo

class LikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Like
        fields = ['id','user','post']
        read_only_fields = ['user']

class CommentSerializer(serializers.ModelSerializer):
    post_s = PostModelSerializer(read_only=True)
    usertag = serializers.CharField(source='user.profile.usertag', read_only=True)
    profile_pic = serializers.CharField(source='user.profile.profile_pic', read_only=True)

    class Meta:
        model = Comment
        fields = '__all__'
        read_only_fields = ['user','usertag']

    # def get_post_auth(self,obj):
    #     return obj.post.user.username



# class LikeSerializer(serializers.ModelSerializer):
#     user = serializers.ReadOnlyField()
#     post_id = serializers.IntegerField()

#     def create(self, validated_data):
#         user = self.request.user
#         post = PostModel.objects.get(id=validated_data['post_id'])
#         post.likes.add(user)
#         return post
#     def delete(self,validated_data):
#         user = self.request.user
#         post = PostModel.objects.get(id=validated_data['post_id'])
#         post.likes.remove(user)
#         return post