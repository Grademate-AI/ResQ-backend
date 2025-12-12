from rest_framework.permissions import BasePermission
from core.utils import enums


class IsGuestUser(BasePermission):
    """
    Allows access only to non-authenticated accounts.
    """

    message: str

    def has_permission(self, request, view):
        self.message = "You are already logged in"
        return not request.user.is_authenticated
    

class IsAccountType:
    class SuperAdminUser(BasePermission):
        """
        Allows access only to super admin users.
        """

        message: str

        def has_permission(self, request, view):
            self.message = "This endpoint is only for super admins"
            return (
                request.user.account_type 
                == enums.UserAccountType.SUPER_ADMIN.value
            )

    class IsVolunteerAccount(BasePermission):
        """
        Allows access only to volunteers.
        """

        message: str

        def has_permission(self, request, view):
            self.message = "You are not a volunteer!"
            return (
                request.user.account_type == enums.UserAccountType.VOLUNTEER.value
            )

    class IsOrganizationAccount(BasePermission):
        """
        Allows access only to Organizations.
        """

        message: str

        def has_permission(self, request, view):
            self.message = "You are not an organization!"
            return (
                request.user.account_type == enums.UserAccountType.ORGANIZATION.value
            )

         
    class IsSuperAdminOrOrganization(BasePermission):
        def has_permission(self, request, view):
            return (
                IsAccountType.SuperAdminUser().has_permission(request, view)
                or IsAccountType.IsOrganizationAccount().has_permission(request, view)
            )
        

class IsObjOwner(BaseException):
    """
    Allows access only to the owner of an object.
    """  
    message: str

    def has_object_permissions(self, request, view, obj):
        self.message = "You do not have permission to access this object."
        return obj.owner == request.user
    