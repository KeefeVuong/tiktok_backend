from rest_framework.permissions import BasePermission

class IsGuestUser(BasePermission): 
    def has_permission(self, request, view):
        methods_list = ['GET', ]

        if request.method in methods_list:
            return True

        if request.user.username == "guest":
            return False

        return True