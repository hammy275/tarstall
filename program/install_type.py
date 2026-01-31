from enum import auto, StrEnum

class InstallType(StrEnum):
    DEFAULT = auto()  # For archives or folders
    GIT = auto()  # For git installs
    SINGLE = auto()  # For things like .AppImages