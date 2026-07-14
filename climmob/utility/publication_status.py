from enum import Enum, IntEnum


def _(x):
    return x


class PublicationStatus(IntEnum):
    INITIAL = 1
    REQUESTED = 2
    # IN_REVIEW = 3 # TODO: update alembic revision
    APPROVED = 4
    REJECTED = 5
    PUBLISHED = 6
    FAILED = 7


class PublicationStatusLabel(Enum):
    INITIAL = "Initial"
    REQUESTED = "Requested"
    # IN_REVIEW = "In review"
    APPROVED = "Approved"
    REJECTED = "Rejected"
    PUBLISHED = "Published"
    FAILED = "Failed"


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
