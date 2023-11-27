from django.db import models
from django.urls import reverse
import uuid

# Create your models here.
class Timestamp(models.Model):
    id = models.UUIDField(primary_key=True,default=uuid.uuid4, editable=False)
    stamp = models.IntegerField()
    stampText = models.TextField()
    isPublic = models.BooleanField()
    movie = models.ForeignKey("movieApp.MovieTestingModel", on_delete=models.CASCADE)
    user = models.ForeignKey("user.User", on_delete=models.CASCADE, null=True)
    class Meta:
        db_table = 'timestamp_timestamp'
        unique_together = ['stamp','movie','user']

    def __str__(self):
        return str(self.stamp) + str(self.movie) + str(self.user)

class TimestampLike(models.Model):
    id = models.UUIDField(primary_key=True,default=uuid.uuid4, editable=False)
    post = models.ForeignKey("timestamp.Timestamp", on_delete=models.CASCADE)
    user = models.ForeignKey("user.User", on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        unique_together = ('post', 'user')

class TimestampComment(models.Model):
    id = models.UUIDField(primary_key=True,default=uuid.uuid4, editable=False)
    post = models.ForeignKey("timestamp.Timestamp", on_delete=models.CASCADE)
    comment = models.TextField()
    user = models.ForeignKey("user.User", on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
