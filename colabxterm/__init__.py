from .xterm import XTerm
from .manager import start
from . import notebook


def load_ipython_extension(ipython):
    notebook._load_ipython_extension(ipython)
