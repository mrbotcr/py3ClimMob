from enum import Enum, IntEnum, auto


class QuestionType(IntEnum):
    TEXT = 1
    DECIMAL = 2
    INTEGER = 3
    GEO_POINT = 4
    SELECT_ONE = 5
    SELECT_MULTIPLE = 6
    PACKAGE_CODE = 7
    FARMER = 8
    RANKING_OF_OPTIONS = 9
    COMPARISON_WITH_CHECK = 10
    GEO_TRACE = 11
    GEO_SHAPE = 12
    DATE = 13
    TIME = 14
    DATETIME = 15
    IMAGE = 16
    AUDIO = 17
    VIDEO = 18
    BARCODE_QR = 19
    LOCATION = 27


class QuestionTypeLabel(Enum):
    TEXT = "Text"
    DECIMAL = "Decimal"
    INTEGER = "Integer"
    GEO_POINT = "GeoPoint"
    SELECT_ONE = "Select one"
    SELECT_MULTIPLE = "Select multiple"
    PACKAGE_CODE = "Package code"
    FARMER = "Farmer"
    RANKING_OF_OPTIONS = "Ranking of options"
    COMPARISON_WITH_CHECK = "Comparison with check"
    GEO_TRACE = "GeoTrace"
    GEO_SHAPE = "GeoShape"
    DATE = "Date"
    TIME = "Time"
    DATETIME = "DateTime"
    IMAGE = "Image"
    AUDIO = "Audio"
    VIDEO = "Video"
    BARCODE_QR = "Barcode/QR"
    LOCATION = "Location"


class QuestionTypeOrder(IntEnum):
    TEXT = auto()
    RANKING_OF_OPTIONS = auto()
    COMPARISON_WITH_CHECK = auto()
    LOCATION = auto()
    DECIMAL = auto()
    INTEGER = auto()
    GEO_POINT = auto()
    SELECT_ONE = auto()
    SELECT_MULTIPLE = auto()
    GEO_TRACE = auto()
    GEO_SHAPE = auto()
    DATE = auto()
    TIME = auto()
    DATETIME = auto()
    IMAGE = auto()
    AUDIO = auto()
    VIDEO = auto()
    BARCODE_QR = auto()
    PACKAGE_CODE = -1  # Not included as an option
    FARMER = -1  # Not included as an option


def is_type_numerical(q_type) -> bool:
    return int(q_type) == QuestionType.DECIMAL or int(q_type) == QuestionType.INTEGER


class QuestionAnonymity(Enum):
    REMOVE = 1
    PSEUDONYM = 2
    RANGE = 3
    NOISE = 4
    MASK = 5
    MONTH_YEAR = 6
