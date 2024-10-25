from rest_framework.permissions import BasePermission

class IsAdminOrManager(BasePermission):
    def has_permission(self, request, view):
        # Allow access only if the user is an admin or manager
        return request.user.is_authenticated and request.user.role in ['admin', 'manager']