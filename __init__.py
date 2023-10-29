import logging

import os
import sys

current_file_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_file_dir)

from .views import Handler
from .main import ItemProvider

logging.info('threema_connector.__init__.py: threema_connector loaded')


