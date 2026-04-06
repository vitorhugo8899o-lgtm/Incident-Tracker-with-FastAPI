from enum import Enum


class IncidentStatus(str, Enum):
    open = 'open'
    in_progress = 'in_progress'
    resolved = 'resolved'
    closed = 'closed'


class IncidentPriority(str, Enum):
    low = 'low'
    medium = 'medium'
    high = 'high'
    critical = 'critical'


class UserRole(str, Enum):
    CLIENT = 'client'
    TECHNICIAN = 'technician'
    SUPERVISOR = 'supervisor'
