class QuestionType:
    TEXT = "1"
    RANKING_OF_OPTIONS = "9"
    COMPARISON_WITH_CHECK = "10"
    LOCATION = "27"
    DECIMAL = "2"
    INTEGER = "3"
    GEOPOINT = "4"
    SELECT_ONE = "5"
    SELECT_MULTIPLE = "6"
    GEOTRACE = "11"
    GEOSHAPE = "12"
    DATE = "13"
    TIME = "14"
    DATETIME = "15"
    IMAGE = "16"
    AUDIO = "17"
    VIDEO = "18"
    BARCODE_QR = "19"


def is_type_numerical(q_type: str) -> bool:
    return q_type == QuestionType.DECIMAL or q_type == QuestionType.INTEGER
