from PyQt4 import QtGui
from ui_licensedialog import Ui_LicenseDialog

class LicenseDialog (QtGui.QDialog, Ui_LicenseDialog):
    def __init__ (self, parent=None):
        super (LicenseDialog, self).__init__ (parent)
        self.setupUi (self)


