from dataclasses import dataclass

__version__ = "2.0.0a0"


@dataclass
class VersionInfo:
    major: int
    minor: int
    micro: int
    releaselevel: str
    serial: int


version_info = VersionInfo(2, 0, 0, "alpha", 0)
