from rest_framework import permissions


class AuthorOnlyPermission(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        return (
            request.method in permissions.SAFE_METHODS or
            ((request.method == 'PATCH' or request.method == 'DELETE') and
             request.user == obj.author)
        )
