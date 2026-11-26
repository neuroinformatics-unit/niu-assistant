from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("niu-assistant")
except PackageNotFoundError:
    # package is not installed
    pass
