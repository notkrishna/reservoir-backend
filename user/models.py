import uuid
from django.db import models
from firebase_admin import auth
from django.contrib.auth.models import AbstractUser
from django.db.models.signals import pre_save
from django.dispatch import receiver


# from fcm_django.models import FCMDevice

# Create your models here.

class User(AbstractUser):
    username = models.CharField(max_length=300,primary_key=True)
    USERNAME_FIELD = 'username'
    class Meta:
        db_table = 'auth_user'

class UserProfileModel(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True, related_name='profile')
    usertag = models.CharField(max_length=30, unique=True)
    bio = models.CharField(default="This is my bio", max_length=150)
    profile_pic = models.URLField(max_length=1000, default='https://sbcf.fr/wp-content/uploads/2018/03/sbcf-default-avatar.png')
    cover_pic = models.URLField(max_length=1000, default='https://img.freepik.com/premium-vector/brick-wall-with-spot-lights-background-style_23-2148639921.jpg')
    # fcm_device = models.ForeignKey(FCMDevice, on_delete=models.CASCADE, null=True)
    # def save(self, *args, **kwargs):
    #     if self.userTag is None:
    #         self.userTag = self.user.username
    #     return super(UserModel, self).save(*args, **kwargs)

    def update(self, instance, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().update(instance,validated_data)
        
    def __str__(self):
        return self.usertag

class UserFollowerModel(models.Model):
    follower = models.ForeignKey(User, on_delete=models.CASCADE, related_name='following')
    following = models.ForeignKey(User,on_delete=models.CASCADE, related_name='followers')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['follower','following']

class UserBlockModel(models.Model):
    blocker = models.ForeignKey(User, on_delete=models.CASCADE, related_name='blocked', db_index=True)
    blocked = models.ForeignKey(User,on_delete=models.CASCADE, related_name='blocker', db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['blocker','blocked']



# class UserNotifications(models.Model):
#     title = models.CharField(max_length=100)
#     body = models.TextField()
#     post_id = models.ForeignKey('posts.PostModel', on_delete=models.CASCADE, blank=True, null=True)
#     timestamp = models.DateTimeField(auto_now_add=True)
#     user = models.ForeignKey(User, on_delete=models.CASCADE)


