from django.db import models
import uuid
# Create your models here.

class Genre(models.Model):
    name = models.CharField(max_length=50, primary_key=True, unique=True)

# class MovieModel(models.Model):
#     class Meta:
#         db_table = 'movieApp_moviemodel'
#     #mid = models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False)
#     movie_name = models.CharField(unique=True,max_length=250)
#     duration = models.PositiveIntegerField(default=0)
#     description = models.TextField(default='')
#     year = models.PositiveIntegerField(default=0)
#     isShow = models.BooleanField(default=False)
#     genres = models.ManyToManyField(Genre)
#     imgUrl = models.URLField(default='https://images.squarespace-cdn.com/content/v1/51cdafc4e4b09eb676a64e68/1470951916671-6BFFPWQEG68L0R9LZL28/McQueen12.jpg')
#     coverImgUrl = models.URLField(default='https://m.media-amazon.com/images/M/MV5BODJhZDU1MDYtMDQ0NS00N2JmLWI2ZDAtMGNmN2RmNWJhNzQ5L2ltYWdlXkEyXkFqcGdeQXVyNjY1OTY4MTk@._V1_.jpg')
#     def __str__(self):
#         return self.movie_name
    


# class SavedMovies(models.Model):
#     movie_name = models.ForeignKey("movieApp.MovieModel", on_delete=models.CASCADE, related_name='saved')
#     user = models.ForeignKey("user.User", on_delete=models.CASCADE)
#     class Meta:
#         unique_together = ['movie_name','user']

# class FollowMovies(models.Model):
#     movie_name = models.ForeignKey("movieApp.MovieModel", on_delete=models.CASCADE, related_name='follow_movie')
#     user = models.ForeignKey("user.User", on_delete=models.CASCADE)
#     class Meta:
#         unique_together = ['movie_name','user']

# class ProgressMovies(models.Model):
#     movie = models.ForeignKey("movieApp.MovieModel", on_delete=models.CASCADE)
#     user = models.ForeignKey("user.User", on_delete=models.CASCADE)
#     isDone = models.BooleanField(default=False)
#     class Meta:
#         unique_together = ['movie','user']

# class MovieList(models.Model):
#     list_name = models.CharField(max_length=300)
#     movie = models.ManyToManyField("movieApp.MovieModel")
#     user = models.ForeignKey("user.User", on_delete=models.CASCADE)
#     created_at = models.DateTimeField(auto_now_add=True)


class MovieTestingModel(models.Model):
    id = models.UUIDField(primary_key=True,default=uuid.uuid4, editable=False)
    movie_name = models.CharField(max_length=500)
    description = models.TextField(blank=True, null=True, default='No description available')
    coverImgUrl = models.CharField(max_length=1000, blank=True, null=True)
    duration = models.IntegerField(default=100, null=True)
    userHasCover = models.BooleanField(default=False)

    class Meta:
        indexes = [
            models.Index(fields=['id'])
        ]


class CastTestingModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    actor = models.CharField(max_length=500, null=True)
    actor_url = models.CharField(max_length=1000, null=True)

class RoleTestingModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    movie = models.ForeignKey(MovieTestingModel, on_delete=models.CASCADE, related_name='movie', null=True)
    actor = models.ForeignKey(CastTestingModel, on_delete=models.CASCADE, related_name='cast', null=True)
    role = models.CharField(max_length=1000, null=True)

class SavedMoviesModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    movie_name = models.ForeignKey("movieApp.MovieTestingModel", on_delete=models.CASCADE, related_name='saved')
    user = models.ForeignKey("user.User", on_delete=models.CASCADE)
    class Meta:
        unique_together = ['movie_name','user']

class FollowMoviesModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    movie_name = models.ForeignKey("movieApp.MovieTestingModel", on_delete=models.CASCADE, related_name='follow_movie')
    user = models.ForeignKey("user.User", on_delete=models.CASCADE)
    class Meta:
        unique_together = ['movie_name','user']

class ProgressMoviesModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    movie = models.ForeignKey("movieApp.MovieTestingModel", on_delete=models.CASCADE)
    user = models.ForeignKey("user.User", on_delete=models.CASCADE)
    isDone = models.BooleanField(default=False)
    class Meta:
        unique_together = ['movie','user']

class MovieListModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    list_name = models.CharField(max_length=300)
    movie = models.ManyToManyField("movieApp.MovieTestingModel")
    user = models.ForeignKey("user.User", on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

# class SavedMoviesModel(models.Model):
#     id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
#     movie_name = models.ForeignKey("movieApp.MovieTestingModel", on_delete=models.CASCADE, related_name='saved')
#     user = models.ForeignKey("user.User", on_delete=models.CASCADE)
#     class Meta:
#         unique_together = ['movie_name','user']

# class FollowMoviesModel(models.Model):
#     id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
#     movie_name = models.ForeignKey("movieApp.MovieTestingModel", on_delete=models.CASCADE, related_name='follow_movie')
#     user = models.ForeignKey("user.User", on_delete=models.CASCADE)
#     class Meta:
#         unique_together = ['movie_name','user']

# class ProgressMoviesModel(models.Model):
#     id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
#     movie = models.ForeignKey("movieApp.MovieTestingModel", on_delete=models.CASCADE)
#     user = models.ForeignKey("user.User", on_delete=models.CASCADE)
#     isDone = models.BooleanField(default=False)
#     class Meta:
#         unique_together = ['movie','user']

# class MovieListModel(models.Model):
#     id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
#     list_name = models.CharField(max_length=300)
#     movie = models.ManyToManyField("movieApp.MovieTestingModel")
#     user = models.ForeignKey("user.User", on_delete=models.CASCADE)
#     created_at = models.DateTimeField(auto_now_add=True)

# class CrewTestingModel(models.Model):
#     id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
#     crew = models.CharField(max_length=500)
#     crew_url = models.CharField(max_length=1000, null=True)


# class CrewRoleTestingModel(models.Model):
#     id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
#     movie = models.ForeignKey(MovieTestingModel, on_delete=models.CASCADE, related_name='movie_crew')
#     crew = models.ForeignKey(CastTestingModel, on_delete=models.CASCADE, related_name='crew')
#     role = models.CharField(max_length=1000, null=True)

#movies = MovieTestingModel.objects.filter(roletestingmodel__actor = "1f7df073-d42c-4904-a52e-ec8a52d343ba")

