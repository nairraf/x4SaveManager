"""Application Bootstrap

bootstraps the application and then loads a new instance
of modules.gui.WindowController, which creates the initial GUI and calls the
Tk mainloop() method which then waits for the events from the displayed GUI.
"""
import sys
from os import path as ospath
from modules.gui import WindowController

# figure our our current filesystem location, and appdend our modules directory
# to the system path. This way we are able to find our gui and app modules
# no matter where we reside in the filesystem pass the path info to the
# WindowController, which starts everything up
approot = ospath.realpath(ospath.dirname(__file__))
moduleroot = ospath.join(approot, "modules")
sys.path.append(moduleroot)

WindowController(approot, moduleroot)
