from enum import Enum, IntEnum


class PublicationStatus(IntEnum):
    INITIAL = 1
    REQUESTED = 2
    IN_REVIEW = 3
    APPROVED = 4
    REJECTED = 5
    PUBLISHED = 6
    FAILED = 7


class PublicationStatusLabel(Enum):
    INITIAL = "Initial"
    REQUESTED = "Requested"
    IN_REVIEW = "In review"
    APPROVED = "Approved"
    REJECTED = "Rejected"
    PUBLISHED = "Published"
    FAILED = "Failed"


class PublicationStatusCanEdit(Enum):
    INITIAL = False
    REQUESTED = True
    IN_REVIEW = True
    APPROVED = False
    REJECTED = False
    PUBLISHED = False
    FAILED = False


class PublicationStatusCanBeSelected(Enum):
    INITIAL = False
    REQUESTED = False
    IN_REVIEW = True
    APPROVED = True
    REJECTED = True
    PUBLISHED = False
    FAILED = False


def get_publication_status_options():
    options = []
    for status in PublicationStatus:
        option = {
            "value": status,
            "label": PublicationStatusLabel[status.name].value,
            "selectable": PublicationStatusCanBeSelected[status.name].value,
            "editable": PublicationStatusCanEdit[status.name].value,
        }
        options.append(option)
    return options
