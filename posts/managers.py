from django.db import models

class PostQuerySet(models.QuerySet):
    def exclude_blocked_users(self, user):
        blocked_users = user.blocked_users.values_list('blocked', flat=True)
        blocked_by_users = user.blocked_by_users.values_list('blocker', flat=True)
        return self.exclude(user__in=blocked_users).exclude(user_id__in=blocked_by_users)

class PostManager(models.Manager):
    def get_queryset(self):
        return PostQuerySet(self.model, using=self._db)

    def exclude_blocked_users(self, user):
        return self.get_queryset().exclude_blocked_users(user)
