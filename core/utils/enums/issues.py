from .base import BaseEnum


class UrgencyLevel(BaseEnum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    

class IssueStatus(BaseEnum):
    OPEN = "open"
    ASSIGNED = "assigned"
    RESOLVED = "resolved"
    CANCELLED = "cancelled"


class IssueCategory(BaseEnum):
    MEDICAL = "medical"
    SAFETY = "safety"
    FINANCIAL = "financial"
    SOCIAL = "social_support"
    ERRAND = "errand"
    EDUCATION = "education"
    CIVIC = "civic"
    ENVIRONMENTAL = "environmental"
    OTHER = "other"


class ProofOfHelpStatus(BaseEnum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"