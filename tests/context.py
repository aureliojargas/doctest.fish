# Workaround to make ../*.py importable
# Idea from https://www.kennethreitz.org/essays/repository-structure-and-python

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# pylint: disable=wrong-import-position,unused-import,unused-variable
import doctester
from doctester import defaults
from doctester import log
