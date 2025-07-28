from enum import Enum


class QuestionType(Enum):
    TEXT = 1
    DECIMAL = 2
    INTEGER = 3
    GEOPOINT = 4
    SELECT_ONE = 5
    SELECT_MULTIPLE = 6
    PACKAGE_CODE = 7
    FARMER = 8
    RANKING_OF_OPTIONS = 9
    COMPARISON_WITH_CHECK = 10
    GEOTRACE = 11
    GEOSHAPE = 12
    DATE = 13
    TIME = 14
    DATETIME = 15
    IMAGE = 16
    AUDIO = 17
    VIDEO = 18
    BARCODE_QR = 19
    LOCATION = 27


def is_type_numerical(q_type) -> bool:
    return (
        int(q_type) == QuestionType.DECIMAL.value
        or int(q_type) == QuestionType.INTEGER.value
    )


class QuestionAnonymity(Enum):
    REMOVE = 1
    PSEUDONYM = 2
    RANGE = 3
    NOISE = 4
    MASK = 5
    MONTH_YEAR = 6
