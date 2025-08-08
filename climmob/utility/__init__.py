from climmob.utility.helpers import *
from climmob.utility.factory import *
from climmob.utility.question import *


def get_enum_as_dict(enum):
    result = {}
    for member in enum:
        result[member.name] = member.value
    return result
