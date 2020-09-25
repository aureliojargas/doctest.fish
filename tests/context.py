# Workaround to make ../*.py importable
# Idea from https://www.kennethreitz.org/essays/repository-structure-and-python

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# pylint: disable=wrong-import-position,unused-import
from doctester import color
from doctester import core
from doctester import defaults
from doctester import log
from doctester import script
from doctester import util
