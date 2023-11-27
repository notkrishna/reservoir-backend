from django.db import models
from django.core.validators import MaxValueValidator,MinValueValidator
import uuid
# Create your models here.
class MovieRatings(models.Model):
    id = models.UUIDField(primary_key=True,default=uuid.uuid4, editable=False)
    movie = models.ForeignKey("movieApp.MovieTestingModel", on_delete=models.CASCADE)
    user = models.ForeignKey("user.User", on_delete=models.CASCADE)
    rating = models.PositiveSmallIntegerField(validators=[MaxValueValidator(5),MinValueValidator(1)])
    review = models.TextField(default='', blank=True, null=True)
    # tag = models.CharField(max_length=30)
    posted_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        unique_together = ['movie','user']


class RatingLike(models.Model):
    id = models.UUIDField(primary_key=True,default=uuid.uuid4, editable=False)
    post = models.ForeignKey("ratings.MovieRatings", on_delete=models.CASCADE)
    user = models.ForeignKey("user.User", on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        unique_together = ('post', 'user')

class RatingComment(models.Model):
    id = models.UUIDField(primary_key=True,default=uuid.uuid4, editable=False)
    post = models.ForeignKey("ratings.MovieRatings", on_delete=models.CASCADE)
    comment = models.TextField()
    user = models.ForeignKey("user.User", on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    # class Meta:
    #     unique_together = ('rating', 'user')