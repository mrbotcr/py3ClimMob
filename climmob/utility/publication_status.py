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
    NOT_REQUESTED = "Not Requested"
    REQUESTED = "Requested"
    APPROVED = "Approved"
    REJECTED = "Rejected"
    PUBLISHED = "Published"
    FAILED = "Failed"
    PARTIAL = "Partial"

class PublicationStatusOption(Enum):
    APPROVED = PublicationStatus.APPROVED
    REJECTED = PublicationStatus.REJECTED


class PublicationStatusOptionsEnabled(Enum):
    APPROVED = False
    REJECTED = True


class PublicationStatusOptionSelectable(Enum):
    APPROVED = True
    REJECTED = True


def get_publication_status_options():
    options = [
        {"value": -1, "label": _("---"), "selectable": True, "editable": False},
        {
            "value": 0,
            "label": _("Choose an option"),
            "selectable": True,
            "editable": True,
        },
    ]

    for status in PublicationStatusOption:
        option = {
            "value": status.value,
            "label": PublicationStatusLabel[status.name].value,
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
    return status_id == PublicationStatus.APPROVED
