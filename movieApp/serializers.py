from decimal import ROUND_UP, Decimal
from rest_framework import serializers
from .models import (
    Genre,
    # MovieModel, 
    # SavedMovies,
    # ProgressMovies,
    # Genre,
    # MovieList,
    # FollowMovies,
    CastTestingModel,
    RoleTestingModel,
    MovieTestingModel,
    SavedMoviesModel,
    ProgressMoviesModel,
    MovieListModel,
    FollowMoviesModel,

)

from ratings.models import MovieRatings
from django.db.models import Avg, Count

from timestamp.models import Timestamp
from timestamp.serializer import TimeStampProgressSerializer, TimeStampSerializer
# from rating

class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ['id','name'] 


class MovieModelSerializer(serializers.ModelSerializer):
    avg_rating = serializers.SerializerMethodField()
    rating_count = serializers.SerializerMethodField()
    saved = serializers.SerializerMethodField()
    progress = serializers.SerializerMethodField()
    following = serializers.SerializerMethodField()
    # genres = serializers.SlugRelatedField(queryset = Genre.objects.all(), many=True, slug_field='name')
    class Meta:
        model = MovieTestingModel
        fields = '__all__'
        lookup_field = 'id'

    def update(self, instance, validated_data):
        instance.userHasCover = validated_data.get('userHasCover',instance.userHasCover)
        instance.save()
        return instance

    def get_avg_rating(self,obj):
        data = MovieRatings.objects.filter(movie=obj)
        if data:
            average_rating = data.aggregate(avg_rating = Avg('rating'))
            avg_rating = Decimal(average_rating['avg_rating']).quantize(Decimal('0.0'), rounding=ROUND_UP)
            return avg_rating
        else:
            return float(0)

    def get_rating_count(self,obj):
        data = MovieRatings.objects.filter(movie=obj)
        if data:
            no_of_ratings = data.aggregate(rating_count = Count('id'))
            return no_of_ratings['rating_count']
        else:
            return int(0)
        
    def get_saved(self,obj):
        curr_user = self.context['request'].user
        ins = SavedMoviesModel.objects.filter(user=curr_user,movie_name=obj.id)
        return True if ins else False
    
    def get_progress(self,obj):
        curr_user = self.context['request'].user
        ins = ProgressMoviesModel.objects.filter(user=curr_user,movie=obj.id)
        return True if ins else False
    
    def get_following(self,obj):
        curr_user = self.context['request'].user
        ins = FollowMoviesModel.objects.filter(user=curr_user,movie_name=obj.id)
        return True if ins else False
    
    

class MovieSnippetSerializer(serializers.ModelSerializer):
    class Meta:
        model = MovieTestingModel
        fields = ['id','coverImgUrl']
        read_only_fields = ['id','coverImgUrl']


class MovieSearchSerializer(serializers.ModelSerializer):
    description = serializers.SerializerMethodField(read_only=True)
    class Meta:
        model = MovieTestingModel
        fields = ['id','movie_name','description', 'coverImgUrl']
    def get_description(self,obj):
        if len(obj.description)>100:
            return obj.description[:100]+'  . . .'
        return obj.description


# class PartialText(serializers.Field):
#     def __init__(self,substring_length, *args, **kwargs):
#         self.substring_length = substring_length
#         super().__init__(*args, **kwargs)
#     def to_representation(self, value):
#         if isinstance(value, str) and len(value) > self.substring_length:
#             return value[:self.substring_length]
#         return value

class MovieListSerializer(serializers.ListSerializer):
    class Meta:
        model = MovieTestingModel
        fields = ('id','movie_name','description')
    


class SavedMovieSerializer(serializers.ModelSerializer):
    movie_title = serializers.CharField(source='movie_name.movie_name', read_only=True)
    coverImgUrl = serializers.CharField(source='movie_name.coverImgUrl', read_only=True)
    class Meta:
        model = SavedMoviesModel
        fields = '__all__'
        read_only_fields = ['user']

class FollowMovieSerializer(serializers.ModelSerializer):
    # movie_name = serializers.StringRelatedField(source='movie_name.movie_name')
    class Meta:
        model = FollowMoviesModel
        fields = '__all__'
        read_only_fields = ['user']






# class MovieModelSerializer(serializers.ModelSerializer):
#     avg_rating = serializers.SerializerMethodField()
#     rating_count = serializers.SerializerMethodField()
#     saved = serializers.SerializerMethodField()
#     progress = serializers.SerializerMethodField()
#     following = serializers.SerializerMethodField()
#     # genres = serializers.SlugRelatedField(queryset = Genre.objects.all(), many=True, slug_field='name')
#     class Meta:
#         model = MovieModel
#         fields = '__all__'
#         lookup_field = 'id'

#     def get_avg_rating(self,obj):
#         data = MovieRatings.objects.filter(movie=obj)
#         if data:
#             average_rating = data.aggregate(avg_rating = Avg('rating'))
#             avg_rating = Decimal(average_rating['avg_rating']).quantize(Decimal('0.0'), rounding=ROUND_UP)
#             return avg_rating
#         else:
#             return float(0)

#     def get_rating_count(self,obj):
#         data = MovieRatings.objects.filter(movie=obj)
#         if data:
#             no_of_ratings = data.aggregate(rating_count = Count('id'))
#             return no_of_ratings['rating_count']
#         else:
#             return int(0)
        
#     def get_saved(self,obj):
#         curr_user = self.context['request'].user
#         ins = SavedMovies.objects.filter(user=curr_user,movie_name=obj.id)
#         return True if ins else False
    
#     def get_progress(self,obj):
#         curr_user = self.context['request'].user
#         ins = ProgressMovies.objects.filter(user=curr_user,movie=obj.id)
#         return True if ins else False
    
#     def get_following(self,obj):
#         curr_user = self.context['request'].user
#         ins = FollowMovies.objects.filter(user=curr_user,movie_name=obj.id)
#         return True if ins else False

# class MovieSnippetSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = MovieModel
#         fields = ['id','coverImgUrl']
#         read_only_fields = ['id','coverImgUrl']

# class MovieSearchSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = MovieModel
#         fields = '__all__'

# class MovieListSerializer(serializers.ListSerializer):
#     class Meta:
#         model = MovieModel
#         fields = ('id','movie_name','CoverImgUrl','imgUrl')

# class SavedMovieSerializer(serializers.ModelSerializer):
#     # movie_name = serializers.StringRelatedField(source='movie_name.movie_name')
#     class Meta:
#         model = SavedMovies
#         fields = '__all__'
#         read_only_fields = ['user']

# class FollowMovieSerializer(serializers.ModelSerializer):
#     # movie_name = serializers.StringRelatedField(source='movie_name.movie_name')
#     class Meta:
#         model = FollowMovies
#         fields = '__all__'
#         read_only_fields = ['user']

# class ProgressMovieDetailSerializer(serializers.ModelSerializer):
#     stamp_list = serializers.SerializerMethodField(read_only=True)
#     class Meta:
#         model = ProgressMovies
#         fields = '__all__'
#         read_only_fields = ['user']

#     def get_stamp_list(self,obj):
#         curr_user = self.context['request'].user
#         stamps = Timestamp.objects.filter(movie = obj.movie, user=curr_user)
#         stamps = TimeStampProgressSerializer(stamps, many=True).data
#         return stamps
    
class ProgressMovieSerializer(serializers.ModelSerializer):
    movie_name = serializers.CharField(source='movie.movie_name', read_only=True)
    duration = serializers.IntegerField(source='movie.duration', read_only=True)
    coverImgUrl = serializers.CharField(source='movie.coverImgUrl', read_only=True)
    last_stamp = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = ProgressMoviesModel
        fields = '__all__'
        read_only_fields = ['user']
    def get_last_stamp(self,obj):
        curr_user = self.context['request'].user
        inst = Timestamp.objects.filter(user=curr_user, movie=obj.movie).order_by('-stamp').first()
        # inst = TimeStampSerializer(inst.stamp)
        if inst:
            return inst.stamp
        else:
            return None


class MovieListSerializer(serializers.ModelSerializer):
    first_movie = serializers.SerializerMethodField()
    is_in_movie = serializers.SerializerMethodField()
    class Meta:
        model = MovieListModel
        fields = ['id', 'list_name','user','created_at','first_movie','is_in_movie']
        read_only_fields = ['movie','user','created_at']
    
    def get_first_movie(self,obj):
        first_obj = obj.movie.all()[:3]
        if first_obj:
            return [movie.coverImgUrl for movie in first_obj]
        else:
            return None
    def get_is_in_movie(self,obj):
        movie_id = self.context.get('movie_id')
        return obj.movie.filter(id=movie_id).exists()

class IsMovieInList(serializers.ModelSerializer):
    coverImgUrl = serializers.SerializerMethodField(read_only=True)
    movie_name = serializers.SerializerMethodField(read_only=True)
    class Meta:
        model = MovieListModel
        fields = ['id','movie', 'coverImgUrl','movie_name']
        read_only_fields = ['id','movie']

    def get_coverImgUrl(self,obj):
        img = obj['coverImgUrl']
        return img
    def get_movie_name(self,obj):
        return obj['movie_name']

    
    
class RoleTestSerializer(serializers.ModelSerializer):
    movie_name = serializers.CharField(source="movie.title")
    actor = serializers.CharField(source="actor.actor")
    class Meta:
        model = RoleTestingModel
        fields = ['movie_name','role','actor']

class MovieTestSerializer(serializers.ModelSerializer):
    class Meta:
        model = MovieTestingModel
        fields = '__all__'
        # obj = MovieList.objects.filter(user=self.request.user)
