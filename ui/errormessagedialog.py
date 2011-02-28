from PyQt4 import QtGui, QtCore
from ui.ui_errormessagedialog import Ui_ErrorMessageDialog

class ErrorMessageDialog (QtGui.QDialog, Ui_ErrorMessageDialog):
    def __init__ (self, message, parent=None):
        super (ErrorMessageDialog, self).__init__ (parent)
        self.setupUi (self)
        self.label.setText (message)


