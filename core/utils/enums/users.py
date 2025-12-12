from core.utils.enums.base import BaseEnum


class UserAccountType(BaseEnum):
    VOLUNTEER = "volunteer"
    ORGANIZATION = "organization"
    SUPER_ADMIN = "super admin"


class OrganizationType(BaseEnum):
    NGO = "ngo"
    RELIGIOUS_ORG = "religious org"
    CHARITY_FOUNDATION = "charity foundation"
    OTHER = "other"

