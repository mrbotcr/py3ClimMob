import re
from enum import Enum, IntEnum, auto


def _(x):
    return x


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
    TEXT = _("Text")
    DECIMAL = _("Decimal")
    INTEGER = _("Integer")
    GEO_POINT = _("GeoPoint")
    SELECT_ONE = _("Select one")
    SELECT_MULTIPLE = _("Select multiple")
    PACKAGE_CODE = _("Package code")
    FARMER = _("Farmer")
    RANKING_OF_OPTIONS = _("Ranking of options")
    COMPARISON_WITH_CHECK = _("Comparison with check")
    GEO_TRACE = _("GeoTrace")
    GEO_SHAPE = _("GeoShape")
    DATE = _("Date")
    TIME = _("Time")
    DATETIME = _("DateTime")
    IMAGE = _("Image")
    AUDIO = _("Audio")
    VIDEO = _("Video")
    BARCODE_QR = _("Barcode/QR")
    LOCATION = _("Location")


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


class QuestionAnonymity(IntEnum):
    REMOVE = 1
    PSEUDONYM = 2
    RANGE = 3
    NOISE = 4
    MASK = 5
    MONTH_YEAR = 6


class QuestionAnonymityLabel(Enum):
    REMOVE = _("Remove")
    PSEUDONYM = _("Pseudonym")
    RANGE = _("Binning")
    NOISE = _("Noise")
    MASK = _("Mask")
    MONTH_YEAR = _("Month-Year")


QA = QuestionAnonymity


class QuestionTypeAnonymity(Enum):
    TEXT = [QA.REMOVE, QA.PSEUDONYM]
    DECIMAL = [QA.REMOVE, QA.RANGE]
    INTEGER = [QA.REMOVE, QA.RANGE]
    GEO_POINT = [QA.REMOVE, QA.NOISE]
    SELECT_ONE = [QA.REMOVE]
    SELECT_MULTIPLE = [QA.REMOVE]
    PACKAGE_CODE = [QA.REMOVE]
    FARMER = [QA.REMOVE]
    RANKING_OF_OPTIONS = [QA.REMOVE]
    COMPARISON_WITH_CHECK = [QA.REMOVE]
    GEO_TRACE = [QA.REMOVE]
    GEO_SHAPE = [QA.REMOVE]
    DATE = [QA.REMOVE, QA.MONTH_YEAR]
    TIME = [QA.REMOVE]
    DATETIME = [QA.REMOVE, QA.MONTH_YEAR]
    IMAGE = [QA.REMOVE]
    AUDIO = [QA.REMOVE]
    VIDEO = [QA.REMOVE]
    BARCODE_QR = [QA.REMOVE]
    LOCATION = [QA.REMOVE]


def get_question_types_with_anonymity_labeled(request):
    result = []
    for q_type in QuestionType:
        order = QuestionTypeOrder[q_type.name].value
        if order == -1:
            continue
        anonymity_opts = []
        for anonymity in QuestionTypeAnonymity[q_type.name].value:
            anonymity_name = QuestionAnonymityLabel[anonymity.name].value
            anonymity_name = request.translate(anonymity_name)
            anonymity_opts.append({"id": anonymity.value, "name": anonymity_name})
        anonymity_opts = sorted(anonymity_opts, key=lambda x: x["id"])
        q_type_name = QuestionTypeLabel[q_type.name].value
        q_type_name = request.translate(q_type_name)
        result.append(
            {
                "id": q_type.value,
                "name": q_type_name,
                "anonymity_opts": anonymity_opts,
                "order": order,
            }
        )
    result = sorted(result, key=lambda x: x["order"])
    return result


def get_question_by_field_name(field_name, questions):
    for q in questions:
        pattern = (
            rf"^"
            rf"({q.question_code}(_[abc])?(_oth)?)|"
            rf"(perf_{q.question_code}_[123])|"
            rf"(char_{q.question_code}_(pos|neg))"
            rf"$"
        )
        # Since the database is using utf8mb4_unicode_ci, it is necessary to ignore case
        if re.fullmatch(pattern, field_name, flags=re.IGNORECASE):
            return q
    return None
