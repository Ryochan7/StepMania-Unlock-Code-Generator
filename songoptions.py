from PyQt4 import QtGui
from ui_songoptions import Ui_SongOptions

class SongOptions (QtGui.QWidget, Ui_SongOptions):
    def __init__ (self, parent=None):
        super (SongOptions, self).__init__ (parent)
        self.setupUi (self)



