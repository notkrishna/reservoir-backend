from user.models import UserBlockModel
from django.core.cache import cache

class CachedIdsMixin:
    def get_cached_ids(self):
        user = self.request.user

        # Check if the cache key exists
        # cache_key = f'blocker_blocking_ids_{user}'
        cache_key = f'blocker_{user}'
        cached_ids = cache.get(cache_key)

        if cached_ids is None:
            # Fetch the blocker and blocking user IDs
            blocker_ids = UserBlockModel.objects.filter(blocked=user).values_list('blocker_id', flat=True)
            blocked_ids = UserBlockModel.objects.filter(blocker=user).values_list('blocked_id', flat=True)

            # Create a new cache entry for the user
            cached_ids = set(blocker_ids) | set(blocked_ids)
            cache.set(cache_key, cached_ids)

        return cached_ids
    
class WriteCachedIdsMixin:
    def get_write_cached_ids(self, post_user):
        user = post_user

        # Check if the cache key exists
        # cache_key = f'blocker_blocking_ids_{user}'
        cache_key = f'blocker_{user}'
        cached_ids = cache.get(cache_key)

        if cached_ids is None:
            # Fetch the blocker and blocking user IDs
            blocker_ids = UserBlockModel.objects.filter(blocked=user).values_list('blocker_id', flat=True)
            blocked_ids = UserBlockModel.objects.filter(blocker=user).values_list('blocked_id', flat=True)

            # Create a new cache entry for the user
            cached_ids = set(blocker_ids) | set(blocked_ids)
            cache.set(cache_key, cached_ids)

        return cached_ids

