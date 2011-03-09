# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'creditsdialog.ui'
#
# Created: Fri Feb 25 00:04:02 2011
#      by: PyQt4 UI code generator 4.7.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_CreditsDialog(object):
    def setupUi(self, CreditsDialog):
        CreditsDialog.setObjectName("CreditsDialog")
        CreditsDialog.setWindowModality(QtCore.Qt.NonModal)
        CreditsDialog.resize(400, 300)
        CreditsDialog.setMinimumSize(QtCore.QSize(400, 300))
        CreditsDialog.setModal(True)
        self.gridLayout = QtGui.QGridLayout(CreditsDialog)
        self.gridLayout.setObjectName("gridLayout")
        self.tabWidget = QtGui.QTabWidget(CreditsDialog)
        self.tabWidget.setObjectName("tabWidget")
        self.tab = QtGui.QWidget()
        self.tab.setObjectName("tab")
        self.gridLayout_2 = QtGui.QGridLayout(self.tab)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.textEdit = QtGui.QTextEdit(self.tab)
        self.textEdit.setObjectName("textEdit")
        self.gridLayout_2.addWidget(self.textEdit, 0, 0, 1, 1)
        self.tabWidget.addTab(self.tab, "")
        self.gridLayout.addWidget(self.tabWidget, 0, 0, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(CreditsDialog)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Close)
        self.buttonBox.setObjectName("buttonBox")
        self.gridLayout.addWidget(self.buttonBox, 1, 0, 1, 1)

        self.retranslateUi(CreditsDialog)
        self.tabWidget.setCurrentIndex(0)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("clicked(QAbstractButton*)"), CreditsDialog.hide)
        QtCore.QMetaObject.connectSlotsByName(CreditsDialog)

    def retranslateUi(self, CreditsDialog):
        CreditsDialog.setWindowTitle(QtGui.QApplication.translate("CreditsDialog", "Credits", None, QtGui.QApplication.UnicodeUTF8))
        self.textEdit.setHtml(QtGui.QApplication.translate("CreditsDialog", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'Ubuntu\'; font-size:11pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Travis Nickles &lt;ryoohki7@yahoo.com&gt;</p></body></html>", None, QtGui.QApplication.UnicodeUTF8))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), QtGui.QApplication.translate("CreditsDialog", "Written By", None, QtGui.QApplication.UnicodeUTF8))

