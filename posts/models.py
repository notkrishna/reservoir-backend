from django.db import models
import uuid

# Create your models here.

# class PostManager(models.Manager):
#     def text_posts(self):
#         return self.filter(post_type='text')
#     def photo_posts(self):
#         return self.filter(post_type='photo')

class PostModel(models.Model):
    id = models.UUIDField(primary_key=True,default=uuid.uuid4, editable=False)
    user = models.ForeignKey("user.User", on_delete=models.CASCADE, db_index=True)
    movie = models.ForeignKey("movieApp.MovieTestingModel", on_delete=models.CASCADE, db_index=True)
    title = models.CharField(max_length=100)
    caption = models.TextField()
    post_type = models.CharField(max_length=10, default="text")
    photo_url = models.URLField(null=True,blank=True, max_length=2000)
    posted_at = models.DateTimeField(auto_now_add=True)
    # class Meta:
    #     abstract = True

    
# class PhotoPost(PostModel):
#     photo_url = models.URLField(null=True,blank=True)

# class TextPost(PostModel):
#     pass

class Like(models.Model):
    id = models.UUIDField(primary_key=True,default=uuid.uuid4, editable=False)
    post = models.ForeignKey("posts.PostModel", on_delete=models.CASCADE)
    user = models.ForeignKey("user.User", on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        unique_together = ('post', 'user')

class Comment(models.Model):
    id = models.UUIDField(primary_key=True,default=uuid.uuid4, editable=False)
    user = models.ForeignKey("user.User", on_delete=models.CASCADE)
    post = models.ForeignKey("posts.PostModel", on_delete=models.CASCADE)
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

