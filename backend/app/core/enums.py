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
    CRYPTO = "crypto"
    STEGO = "stego"
    ATTACK = "attack"
    ANOMALY = "anomaly"


class CryptoAlgorithm(str, Enum):
    CUSTOM_SPN = "custom_spn"
    AES_256_GCM = "aes-256-gcm"


class CryptoOperationType(str, Enum):
    ENCRYPT = "encrypt"
    DECRYPT = "decrypt"
    STEGO_EMBED = "stego_embed"
    STEGO_EXTRACT = "stego_extract"
    METRIC_AVALANCHE = "metric_avalanche"
    METRIC_STATISTICAL = "metric_statistical"
    ATTACK_BRUTE_FORCE = "attack_brute_force"
    ATTACK_DIFFERENTIAL = "attack_differential"
    ATTACK_STATISTICAL = "attack_statistical"


class CryptoInputKind(str, Enum):
    TEXT = "text"
    FILE = "file"


class AttackType(str, Enum):
    BRUTE_FORCE = "brute_force"
    DIFFERENTIAL = "differential"
    STATISTICAL = "statistical"


class AnomalyType(str, Enum):
    AUTH_BURST = "auth_burst"
    DECRYPT_FAIL_RATE = "decrypt_fail_rate"
    FILE_INTEGRITY = "file_integrity"
    ACCESS_PATTERN = "access_pattern"
    EVENT_SPIKE = "event_spike"


class AnomalySeverity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
