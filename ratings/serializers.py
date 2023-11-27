from rest_framework import serializers

from user.models import User, UserProfileModel
from .models import MovieRatings, RatingLike, RatingComment
from user.serializer import UserModelSerializer

class MovieRatingsSerializer(serializers.ModelSerializer):
    usertag = serializers.CharField(source="user.profile.usertag",read_only=True)
    profile_pic = serializers.URLField(source="user.profile.profile_pic", read_only=True)
    movie = serializers.PrimaryKeyRelatedField(read_only=True)
    movie_name = serializers.CharField(source="movie.movie_name", read_only=True)
    review = serializers.CharField(required=False)
    coverImgUrl = serializers.CharField(source="movie.coverImgUrl", read_only=True)
    # isReviewed = serializers.SerializerMethodField(read_only = True)
    comment_count = serializers.SerializerMethodField(read_only=True)
    like_count = serializers.SerializerMethodField(read_only=True)
    is_liked = serializers.SerializerMethodField(read_only=True)  
    class Meta:
        model = MovieRatings
        fields = '__all__'
        read_only_fields = ['user','usertag','posted_at','comment_count', 'coverImgUrl', 'like_count', 'is_liked',]
    def get_comment_count(self,obj):
        comment_count = RatingComment.objects.filter(post=obj.id).count()
        return comment_count
    def get_like_count(self,obj):
        return RatingLike.objects.filter(post=obj).count()
    def get_is_liked(self,obj):
        curr_user = self.context['request'].user
        return RatingLike.objects.filter(post=obj,user=curr_user).exists()
 


class RatingLikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = RatingLike
        fields = ['id','user','post']
        read_only_fields = ['user']

class RatingCommentSerializer(serializers.ModelSerializer):
    usertag = serializers.CharField(source="user.profile.usertag",read_only=True)
    profile_pic = serializers.CharField(source="user.profile.profile_pic", read_only=True)
    class Meta:
        model = RatingComment
        fields = ['id','user','post','comment','usertag','profile_pic']
        read_only_fields = ['id','user']
