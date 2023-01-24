from modules.gui import WindowController
from os.path import realpath, dirname

approot = realpath(dirname(__file__))

WindowController(approot)