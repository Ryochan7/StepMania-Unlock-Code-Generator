# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui/errormessagedialog.ui'
#
# Created: Sun Feb 27 12:50:29 2011
#      by: PyQt4 UI code generator 4.7.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_ErrorMessageDialog(object):
    def setupUi(self, ErrorMessageDialog):
        ErrorMessageDialog.setObjectName("ErrorMessageDialog")
        ErrorMessageDialog.resize(500, 200)
        ErrorMessageDialog.setMinimumSize(QtCore.QSize(500, 200))
        self.verticalLayout = QtGui.QVBoxLayout(ErrorMessageDialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.label = QtGui.QLabel(ErrorMessageDialog)
        self.label.setFrameShape(QtGui.QFrame.NoFrame)
        self.label.setTextFormat(QtCore.Qt.AutoText)
        self.label.setScaledContents(True)
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setWordWrap(True)
        self.label.setObjectName("label")
        self.verticalLayout.addWidget(self.label)
        self.buttonBox = QtGui.QDialogButtonBox(ErrorMessageDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Close)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(ErrorMessageDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("accepted()"), ErrorMessageDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("rejected()"), ErrorMessageDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(ErrorMessageDialog)

    def retranslateUi(self, ErrorMessageDialog):
        ErrorMessageDialog.setWindowTitle(QtGui.QApplication.translate("ErrorMessageDialog", "Message", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("ErrorMessageDialog", "Example Text", None, QtGui.QApplication.UnicodeUTF8))

