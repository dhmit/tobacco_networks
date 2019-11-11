"""
Helper file, currently makes path to DATA_PATH available

"""

import os
from pathlib import Path

DATA_PATH = Path(Path(os.path.abspath(os.path.dirname(__file__))).parent, 'data')
