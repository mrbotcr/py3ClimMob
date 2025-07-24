from enum import Enum


class ProjectAccessType(Enum):
    OWNER = 1
    ADMIN = 2
    EDITOR = 3
    MEMBER = 4


class ProjectAdmin(Enum):
    YES = 1
    NO = 0


class ProjectClimMobAnalytics(Enum):
    VERIFY = 2
    YES = 1
    NO = 0


class ProjectActive(Enum):
    YES = 1
    NO = 0


class ProjectChecked(Enum):
    YES = 1
    NO = 0


def project_access_type_get_dict():
    return {opt.name.capitalize(): opt.value for opt in ProjectAccessType}


def project_admin_get_dict():
    return {opt.name.capitalize(): opt.value for opt in ProjectAccessType}


def project_climmob_analytics_get_dict():
    return {opt.name.capitalize(): opt.value for opt in ProjectClimMobAnalytics}


def project_active_get_dict():
    return {opt.name.capitalize(): opt.value for opt in ProjectActive}


def project_checked_get_dict():
    return {opt.name.capitalize(): opt.value for opt in ProjectChecked}
