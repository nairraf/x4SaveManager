from modules.gui import MainWindow
from os.path import realpath, dirname

approot = realpath(dirname(__file__))

MainWindow(approot)