from enum import Enum


class UserRole(str, Enum):
    CANDIDATE = "candidate"
    RECRUITER = "recruiter"
    ADMIN = "admin"


class JobStatus(str, Enum):
    OPEN = "open"
    CLOSED = "closed"


class EmploymentType(str, Enum):
    FULL_TIME = "full_time"
    PART_TIME = "part_time"
    CONTRACT = "contract"
    INTERNSHIP = "internship"
    REMOTE = "remote"


class ApplicationStatus(str, Enum):
    SUBMITTED = "submitted"
    REVIEWING = "reviewing"
    INTERVIEW = "interview"
    APPROVED = "approved"
    REJECTED = "rejected"


class SecurityEventType(str, Enum):
    AUTH = "auth"
    USER = "user"
    PROFILE = "profile"
    RESUME = "resume"
    JOB = "job"
    APPLICATION = "application"
    AI = "ai"
    ADMIN = "admin"
    ACCESS = "access"
