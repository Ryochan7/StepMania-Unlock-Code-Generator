from PyQt4 import QtGui
from ui_creditsdialog import Ui_CreditsDialog

class CreditsDialog (QtGui.QDialog, Ui_CreditsDialog):
    def __init__ (self, parent=None):
        super (CreditsDialog, self).__init__ (parent)
        self.setupUi (self)


