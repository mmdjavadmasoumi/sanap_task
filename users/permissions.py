from rest_framework.permissions import BasePermission

class IsInstructor(BasePermission):


    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.user_type == 1  # 1 corresponds to Instructor in UserType
