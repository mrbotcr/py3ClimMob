from enum import Enum


class ProjectAccessType(Enum):
    OWNER = 1
    ADMIN = 2
    EDITOR = 3
    MEMBER = 4
