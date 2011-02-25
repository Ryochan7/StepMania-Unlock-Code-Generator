from PyQt4 import QtGui, QtCore
import webbrowser
from ui_aboutdialog import Ui_AboutDialog
from licensedialog import LicenseDialog
from creditsdialog import CreditsDialog

class AboutDialog (QtGui.QDialog, Ui_AboutDialog):
    def __init__ (self, parent=None):
        super (AboutDialog, self).__init__ (parent)
        self.setupUi (self)
        self.license_dialog = LicenseDialog ()
        self.credits_dialog = CreditsDialog ()
        self.licenseButton.clicked.connect (self.license_dialog.show)
        self.label.linkActivated.connect (self.open_link)
        self.creditsButton.clicked.connect (self.credits_dialog.show)

    @QtCore.pyqtSlot ("QString")
    def open_link (self, url):
        webbrowser.open (url)

