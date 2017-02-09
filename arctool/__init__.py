"""arctool package."""

__version__ = "0.12.0"

from jinja2 import ChoiceLoader, PackageLoader

from dtool.utils import JINJA2_ENV


JINJA2_ENV.loader = ChoiceLoader([
    PackageLoader("dtool", "templates"),
    PackageLoader("arctool", "templates"),
])
