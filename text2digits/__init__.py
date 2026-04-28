from importlib.metadata import version, PackageNotFoundError

from text2digits.text2digits import Text2Digits

name = "text2digits"

try:
    __version__ = version("text2digits")
except PackageNotFoundError:
    __version__ = "unknown"

__all__ = ['Text2Digits']
