# Copyright (c) 2011 Adi Roiban.
# See LICENSE for details.
'''Commons modules used by Chevah components.'''

# These modules are required to be loaded first, as on some platforms
# Python failed to load them later.
import hashlib
# Silence the linter.
hashlib
import os

MODULE_PATH = os.path.dirname(__file__)
# Silence the linter.
MODULE_PATH

if os.name == 'nt':
    # On Windows, pythoncom must be loaded first to fix DLL path loading.
    import pythoncom
    pythoncom

# Create EventsHandler singleton and add method shortcuts.
from chevah.utils.event import EventsHandler
events_handler = EventsHandler()
emit = events_handler.emit
log = events_handler.log
