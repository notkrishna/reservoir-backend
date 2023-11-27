
# from django.db.models.signals import post_save
# from django.dispatch import receiver
# from fcm_django.models import FCMDevice
# from .models import Comment,Like
# from user.models import UserNotifications, UserProfileModel
# from firebase_admin.messaging import Message,Notification
# from celery import shared_task
# import logging


# # @shared_task
# @receiver(post_save, sender=Comment)
# def send_comment_notification(sender, instance, created, **kwargs):
#     #To handle celery ops
#     # try:
#         if created:
#             # Get the user who posted the comment
#             user = instance.user
#             user_profile= UserProfileModel.objects.get(user=user)
#             posted_by = instance.post
            
#             # Get the FCM device registration token for the user
#             fcm_device = FCMDevice.objects.filter(user=posted_by.user).first()
            
#             if fcm_device and user != posted_by.user:

#                 message = Message(
#                     notification=Notification(
#                         title='New Comment',
#                         body= f'{user_profile.usertag} commented on your post.',
#                     )
#                 )
#                 # Create a notification payload
#                 # message = {
#                 #     'title': 'New comment',
#                 #     'body': f'{user.username} posted a new comment',
#                 #     # 'data': {
#                 #     #     'comment_id': str(instance.pk),
#                 #     # },
#                 # }
                
#                 UserNotifications.objects.create(
#                     post_id = instance.post.id,
#                     user = posted_by.user,
#                     title = 'New Comment',
#                     body = f'{user_profile.usertag} commented on your post.'
                    
#                 )

#                 # Send the notification to the user's device
#                 fcm_device.send_message(message)
#     # except Exception as e:
#     #     logging.error(f"Failed to send notif")

# @receiver(post_save, sender=Like)
# def send_comment_notification(sender, instance, created, **kwargs):
#     if created:
#         # Get the user who posted the comment
#         user = instance.user
#         user_profile= UserProfileModel.objects.get(user=user)
#         posted_by = instance.post
        
#         # Get the FCM device registration token for the user
#         fcm_device = FCMDevice.objects.filter(user=posted_by.user).first()
        
#         if fcm_device and user!=posted_by.user:

#             message = Message(
#                 notification=Notification(
#                     title=f'{user_profile.usertag}',
#                     body= f'liked your post.',
#                 )
#             )
#             # Create a notification payload
#             # message = {
#             #     'title': 'New comment',
#             #     'body': f'{user.username} posted a new comment',
#             #     # 'data': {New Comment
#             #     #     'comment_id': str(instance.pk),
#             #     # },
#             # }
            
#             UserNotifications.objects.create(
#                 user = posted_by.user,
#                 title = f'{user_profile.usertag}',
#                 body = f'liked your post.',
#                 post_id = posted_by
#             )

#             # Send the notification to the user's device
#             fcm_device.send_message(message)
