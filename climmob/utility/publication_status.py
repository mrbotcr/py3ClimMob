from enum import Enum, IntEnum


def _(x):
    return x


class PublicationStatus(IntEnum):
    NOT_REQUESTED = 1
    REQUESTED = 2
    APPROVED = 3
    REJECTED = 4
    PUBLISHED = 5
    FAILED = 6
    PARTIAL = 7


class PublicationStatusLabel(Enum):
    NOT_REQUESTED = _("Not Requested")
    REQUESTED = _("Requested")
    APPROVED = _("Approved")
    REJECTED = _("Rejected")
    PUBLISHED = _("Published")
    FAILED = _("Failed")
    PARTIAL = _("Partial")


class PublicationApproved(IntEnum):
    DEFAULT = 0
    APPROVED = 1
    REJECTED = 2


class PublicationStatusOptionLabel(Enum):
    DEFAULT = _("Choose an option")
    APPROVED = _("Approved")
    REJECTED = _("Rejected")


class PublicationStatusOptionsEnabled(Enum):
    DEFAULT = True
    APPROVED = False
    REJECTED = True


class PublicationStatusOptionSelectable(Enum):
    DEFAULT = True
    APPROVED = True
    REJECTED = True


def get_publication_status_options():
    options = [
        {"value": -1, "label": _("---"), "selectable": True, "editable": False},
    ]

    for status in PublicationApproved:
        option = {
            "value": status.value,
            "label": PublicationStatusOptionLabel[status.name].value,
            "selectable": PublicationStatusOptionSelectable[status.name].value,
            "editable": PublicationStatusOptionsEnabled[status.name].value,
        }
        options.append(option)
    return options


def is_status_requestable(status_id):
    return status_id == PublicationStatus.NOT_REQUESTED


def is_status_approvable(status_id):
    return (
        status_id == PublicationStatus.REQUESTED
        or status_id == PublicationStatus.REJECTED
    )


def is_status_rejectable(status_id):
    return status_id == PublicationStatus.REQUESTED


def is_status_publishable(status_id):
    return (
        status_id == PublicationStatus.APPROVED or status_id == PublicationStatus.FAILED
    )
