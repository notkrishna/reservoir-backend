from django.core.cache import cache
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import UserBlockModel

# @receiver([post_save, post_delete], sender=UserBlockModel)
# def invalidate_cache(sender, instance, **kwargs):
#     # Invalidate cache for the current user (blocker or blocked)
#     curr_user = instance.blocker  # Assuming the current user is the blocker
#     curr_user.invalidate_cached_ids()
