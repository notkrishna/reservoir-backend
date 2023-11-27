from rest_framework.permissions import BasePermission

from user.models import UserBlockModel

class OwnerPermission(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in ['GET','HEAD','OPTIONS']:
            return True
        return obj.user == request.user

class IsBlockedOrBlocker(BasePermission):
    def has_permission(self, request, view):
        # Check if the requesting user is blocked by the owner of the resource
        blocked_users = UserBlockModel.objects.filter(blocker=request.user).values_list('blocked', flat=True)
        if request.user in blocked_users:
            return False

        # Check if the requesting user is blocking the owner of the resource
        blocking_users = UserBlockModel.objects.filter(blocked=request.user).values_list('blocker', flat=True)
        if request.user in blocking_users:
            return False

        print(blocked_users)
        print(blocking_users)
        
        return True
        

    def has_object_permission(self, request, view, obj):
        # Assuming the resource has an owner field indicating the user who owns it
        owner = request.user

        # Check if the requesting user is blocked by the owner of the resource
        blocked_users = UserBlockModel.objects.filter(blocker=request.user)

        # Check if the requesting user is blocking the owner of the resource
        blocking_users = UserBlockModel.objects.filter(blocked=request.user)
        if blocked_users.exists() or blocking_users.exists():
            return False

        return True
    
class HideBlockedContentPermission(BasePermission):
    def has_permission(self, request, view):
        user = request.user

        blocked_user_ids = getattr(request, 'blocked', [])
        blocked_by_user_ids = getattr(request, 'blocker', [])

        return user.username not in blocked_user_ids and user.username not in blocked_by_user_ids
