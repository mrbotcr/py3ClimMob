from enum import Enum


class ProjectAccessType(Enum):
    OWNER = 1
    ADMIN = 2
    EDITOR = 3
    MEMBER = 4


class ProjectStatus(Enum):
    UNDEFINED = 0
    DEFINITION = 1
    IN_PROGRESS = 2
    FINALIZED = 3
