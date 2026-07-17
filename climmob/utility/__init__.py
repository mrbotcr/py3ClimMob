import importlib
import inspect
import pkgutil

from climmob.utility.anonymization import *
from climmob.utility.email import *
from climmob.utility.factory import *
from climmob.utility.helpers import *
from climmob.utility.publication_status import *
from climmob.utility.question import *
from climmob.utility.request import *


def get_enum_as_dict(enum):
    result = {}
    for member in enum:
        result[member.name] = member.value
    return result


def add_enums_to_context(event):
    """Finds all Enums in this package and adds them to the Jinja event context."""
    # Use globals() to get this package's path and name dynamically
    package_path = globals()["__path__"]
    package_name = globals()["__name__"]

    # 1. Walk through all modules inside this package folder
    for module_info in pkgutil.walk_packages(package_path, package_name + "."):

        # 2. Dynamically import the sub-module (e.g., "myapp.enums.users")
        module = importlib.import_module(module_info.name)

        # 3. Look for Enums inside the imported module
        for name, obj in inspect.getmembers(module):
            if (
                inspect.isclass(obj)
                and issubclass(obj, Enum)
                and obj is not Enum
                and obj is not IntEnum
            ):
                event[name] = obj
