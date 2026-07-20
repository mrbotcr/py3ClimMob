from enum import Enum, IntEnum


class PublicationLicense(IntEnum):
    CC0 = 1
    CC_BY = 2
    CC_BY_SA = 3


class PublicationLicenseLabel(Enum):
    CC0 = "CC-0"
    CC_BY = "CC-BY4.0"
    CC_BY_SA = "CC-BY-SA-4.0"
