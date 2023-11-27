from rest_framework import serializers
from .models import Timestamp, TimestampLike, TimestampComment

from user.serializer import UserDetailSnippetSerializer

class TimeStampSerializer(serializers.ModelSerializer):
    movie_name = serializers.CharField(source="movie.movie_name", read_only = True)
    usertag = serializers.CharField(source="user.profile.usertag",read_only=True)
    # usertag = UserDetailSnippetSerializer()
    coverImgUrl = serializers.CharField(source="movie.coverImgUrl", read_only = True)
    comment_count = serializers.SerializerMethodField(read_only=True)
    is_liked = serializers.SerializerMethodField(read_only=True)
    like_count = serializers.SerializerMethodField(read_only=True)
    class Meta:
        model = Timestamp
        fields = '__all__'
        read_only_fields = ['user','usertag']

    def get_like_count(self,obj):
        return TimestampLike.objects.filter(post=obj).count()
    def get_is_liked(self,obj):
        curr_user = self.context['request'].user
        return TimestampLike.objects.filter(post=obj,user=curr_user).exists()
    def get_comment_count(self,obj):
        try:
            comment_count = TimestampComment.objects.filter(post=obj.id).count()
            return comment_count
        except:
            return 0


class TimeStampProgressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Timestamp
        fields = ['id','stamp','stampText']
        read_only_fields = ['id']

class TimestampLikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = TimestampLike
        fields = ['id','user','post']
        read_only_fields = ['user']

class TimestampCommentSerializer(serializers.ModelSerializer):
    usertag = serializers.CharField(source = 'user.profile.usertag', read_only=True)
    profile_pic = serializers.CharField(source = 'user.profile.profile_pic', read_only=True)
    class Meta:
        model = TimestampComment
        fields = ['id','user','post','comment','usertag','profile_pic']
        read_only_fields = ['id','user','usertag']