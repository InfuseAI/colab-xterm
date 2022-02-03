from .xterm import XTerm
from .notebook import load_ipython_extension

import os
def _get_version():
    version_file = os.path.normpath(os.path.join(os.path.dirname(__file__), 'VERSION'))
    with open(version_file) as fh:
        version = fh.read().strip()
        return version

__version__ = _get_version()
