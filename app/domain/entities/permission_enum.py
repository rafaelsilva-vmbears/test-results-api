from enum import Enum

class Permission(str, Enum):
    READ = "READ"
    WRITE = "WRITE"
    ADMIN = "ADMIN"
