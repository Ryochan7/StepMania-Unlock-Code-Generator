#!/usr/bin/env python

import os
import sys
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from stepmaniaunlock.ui.ui_mainwindow import Ui_MainWindow
from stepmaniaunlock.ui.aboutdialog import AboutDialog
from stepmaniaunlock.ui.errormessagedialog import ErrorMessageDialog
from stepmaniaunlock.controllers.loadsongs_controller import LoadSongsController
from stepmaniaunlock.controllers.writeunlock_controller import WriteUnlockController
from stepmaniaunlock.controllers.readunlock_controller import ReadUnlockController

class CustomTreeWidgetItem (QTreeWidgetItem):
    def __init__ (self, parent=None):
        super (CustomTreeWidgetItem, self).__init__ (parent)
        self.group = self.song = None

    def __lt__ (self, other):
        string1 = unicode (self.text (0)).lower ()
        string2 = unicode (other.text (0)).lower ()
        # Count self as greater. Will appear first in ascending order
        if string1 == string2:
            return False

        string1_length = len (string1)
        string2_length = len (string2)

        shorter_string = string2
        if string1_length <= string2_length:
            shorter_string = string1

        for i, char in enumerate (shorter_string):
            if string1[i] != string2[i]:
                return string1[i] < string2[i]

        # Count smaller string as greater. Will appear first in
        # ascending order
        return False

class UnlockItem (QStandardItem):
    def __init__ (self, text=None):
        super (self.__class__, self).__init__ (text)
        self.group = self.song = None

    def __lt__ (self, other):
        #print "IN HERE"
        string1 = unicode (self.text ()).lower ()
        string2 = unicode (other.text ()).lower ()
        # Count self as greater. Will appear first in ascending order
        if string1 == string2:
            return False

        string1_length = len (string1)
        string2_length = len (string2)

        shorter_string = string2
        if string1_length <= string2_length:
            shorter_string = string1

        for i, char in enumerate (shorter_string):
            if string1[i] != string2[i]:
                return string1[i] < string2[i]

        # Count smaller string as greater. Will appear first in
        # ascending order
        return False

class UnlockModel (QStandardItemModel):
    GROUPITEMS = 1
    SONGITEMS = 2

    def __init__ (self, datalist=None, unlocktype=SONGITEMS, parent=None):
        super (UnlockModel, self).__init__ (parent)
        self.group = self.song = None
        header_text = "Groups" if unlocktype == self.GROUPITEMS else "Songs"
        self.setHorizontalHeaderLabels ([header_text])
        datalist = datalist if datalist else list ()
        for item in datalist:
            newitem = UnlockItem (item.name)
            if unlocktype == self.GROUPITEMS:
                newitem.group = item
            elif unlocktype == self.SONGITEMS:
                newitem.song = item
            self.appendRow (newitem)

class CustomSortFilterProxyModel (QSortFilterProxyModel):
    def __init__ (self, parent=None):
        super (self.__class__, self).__init__ (parent)
        self.setSortCaseSensitivity (Qt.CaseInsensitive)
        self.setFilterCaseSensitivity (Qt.CaseInsensitive)

    def data (self, index, role):
        if not index.isValid ():
            return QVariant ()

        if role == Qt.DisplayRole:
            return super (self.__class__, self).data (index, role)
        elif role == Qt.UserRole:
            source_index = self.mapToSource (index)
            return QVariant (source_index.model ().itemFromIndex (source_index))

        return QVariant ()

class MainWindow (QMainWindow, Ui_MainWindow):
    def __init__ (self, parent=None):
        super (MainWindow, self).__init__ (parent)
        self.setupUi (self)
        self.progressbar = QProgressBar (self)
        self.progressbar.setRange (0, 100)
        self.progressbar.setMaximumSize (QSize (200, 20))
        self.statusbar.addPermanentWidget (self.progressbar)
        self.aboutdialog = AboutDialog ()
        # Leave old example of signal handling
        self.connect (self.actionQuit, SIGNAL ("triggered ()"),
            qApp, SLOT ("quit ()"))
        self.actionAbout.triggered.connect (self.aboutdialog.show)
        #self.actionQuit.triggered.connect (qApp.quit)
        self.in_reset = False
        self.group_collection = []
        self.songOptionsFrame.hide ()
        self.filterFrame.hide ()
        self.treeWidget.clear ()

        self.unlock_model = UnlockModel ([], UnlockModel.SONGITEMS)
        self.filter_unlock_model = CustomSortFilterProxyModel (self)
        self.filter_unlock_model.setSourceModel (self.unlock_model)
        self.treeView.setModel (self.filter_unlock_model)
        self.treeView.selectionModel ().currentChanged.connect (self.on_treeView_currentItemChanged)
        self.lineEdit_2.textChanged.connect (self.treeView_filter)

        item = CustomTreeWidgetItem (["All"])
        itfont = QFont ()
        itfont.setBold (True)
        item.setFont (0, itfont)
        self.treeWidget.addTopLevelItem (item)
        self.all_item = item

        self.treeWidget.sortItems (0, Qt.AscendingOrder)
        self.treeView.sortByColumn (0, Qt.AscendingOrder)

    @pyqtSlot ()
    def on_toolButton_clicked (self):
        fileName = QFileDialog.getExistingDirectory (self,
            "Choose StepMania Directory", os.path.dirname (sys.argv[0]))

        if fileName:
            self.lineEdit.setText (fileName)
            self.loadSongsButton.setEnabled (True)

    @pyqtSlot ()
    def on_loadSongsButton_clicked (self):
        searchfolder = str(self.lineEdit.text ())
        if not searchfolder:
            # No directory selected. Return
            return
        elif not os.path.isdir (os.path.join (searchfolder, "Songs")):
            return

        self.treeWidget.clear ()
        self.treeView.reset ()
        self.treeView.setModel (QStandardItemModel ())

        self.songOptionsFrame.setEnabled (False)
        self.loadSongsButton.setEnabled (False)
        self.toolButton.setEnabled (False)
        self.filterFrame.setEnabled (False)
        self.progressbar.setValue (0)
        self.progressbar.show ()

        self.group_collection = []
        controller = LoadSongsController (searchfolder, self.group_collection, self)
        controller.groupload_notice.connect (self.statusbar.showMessage)
        controller.finished.connect (self.songOptionsFrame.show)
        controller.finished.connect (self.populateTreeWidgets)
        controller.smfileread_complete.connect (self.progressbar.setValue)
        controller.start ()

    @pyqtSlot ()
    def populateTreeWidgets (self):
        for i, group in enumerate (self.group_collection):
            item = CustomTreeWidgetItem ([group.name])
            if i == 0:
                itfont = QFont ()
                itfont.setBold (True)
                item.setFont (0, itfont)
                self.all_item = item
                songs = group.songs

            item.group = group
            self.treeWidget.addTopLevelItem (item)

        searchfolder = str(self.lineEdit.text ())
        controller = ReadUnlockController (searchfolder, songs)
        controller.run ()

        self.treeWidget.setCurrentItem (self.all_item)
        self.songOptionsFrame.setEnabled (True)
        self.loadSongsButton.setEnabled (True)
        self.toolButton.setEnabled (True)
        self.filterFrame.setEnabled (True)
        self.filterFrame.show ()
        self.progressbar.hide ()

        self.group_collection = []

    @pyqtSlot (str)
    def display_error_message (self, message):
        error_dialog = ErrorMessageDialog (message)
        error_dialog.exec_ ()

    @pyqtSlot (str)
    def display_exit_message (self, message):
        error_dialog = ErrorMessageDialog (message)
        error_dialog.setWindowTitle ("Exiting")
        error_dialog.exec_ ()

    @pyqtSlot ()
    def on_cancelButton_clicked (self):
        # self.songOptionsFrame.hide ()
        qApp.quit ()

    @pyqtSlot ()
    def on_resetButton_clicked (self):
        self.in_reset = True
        self.treeView.clearSelection ()
        self.treeView.reset ()
        self.treeWidget.clearSelection ()
        self.treeWidget.reset ()

        self.treeWidget.scrollToTop ()
        topitem = self.treeWidget.topLevelItem (0)
        self.treeWidget.setCurrentItem (topitem)

        iterator = QTreeWidgetItemIterator (self.treeWidget)
        while (iterator.value ()):
            iteritem = iterator.value ()
            iteritem.group.reset ()
            iterator += 1

        self.in_reset = False

    @pyqtSlot ()
    def on_saveButton_clicked (self):
        searchfolder = str(self.lineEdit.text ())

        groupitem = self.treeWidget.currentItem ()
        song_index = self.treeView.currentIndex ()
        songitem = song_index.data (Qt.UserRole).toPyObject ()
        # Check for selected song first
        if songitem:
            song = songitem.song
            song.arcade = self.songOptionsWidget.arcadeSpinBox.value ()
            song.clear = self.songOptionsWidget.clearSpinBox.value ()
            song.dance = self.songOptionsWidget.danceSpinBox.value ()
            song.roulette = self.songOptionsWidget.rouletteSpinBox.value ()
            song.song = self.songOptionsWidget.spointsSpinBox.value ()
        # Check if only a group is selected
        elif groupitem:
            group = groupitem.group
            #print group
            if self._group_update_needed (group):
                self._group_update (group)
                group.change_songs ()

        # Save final data
        controller = WriteUnlockController (searchfolder, self.all_item.group.songs)
        controller.error.connect (self.display_exit_message)
        controller.success.connect (self.display_exit_message)
        controller.run ()

        qApp.quit ()

    # Handle cursor change events
    @pyqtSlot ("QTreeWidgetItem*", "QTreeWidgetItem*")
    def on_treeWidget_currentItemChanged (self, current, previous):
        if not current and not previous:
            # Widget cleared. No previous selection. Ignore
            return
        elif not current or not current.group:
            # Initial item with group set to None
            return

        if previous and not self.in_reset and not self.treeView.currentIndex ():
            group = previous.group
            #print group
            if self._group_update_needed (group):
                self._group_update (group)
                group.change_songs ()

        self.treeView.reset ()
        self.treeView.scrollToTop ()

        self.unlock_model = UnlockModel (current.group.songs, UnlockModel.SONGITEMS, self)
        self.filter_unlock_model = CustomSortFilterProxyModel (self)
        self.filter_unlock_model.setSourceModel (self.unlock_model)
        self.treeView.setModel (self.filter_unlock_model)
        # Reset made new selection model. Connect slot again
        self.treeView.selectionModel ().currentChanged.connect (self.on_treeView_currentItemChanged)

        self.songOptionsWidget.itemLabel.setText (self.tr ("Group Name:"))
        self.songOptionsWidget.lineEdit_2.setText (current.group.name)
        self.songOptionsWidget.arcadeSpinBox.setValue (current.group.values[0])
        self.songOptionsWidget.clearSpinBox.setValue (current.group.values[1])
        self.songOptionsWidget.danceSpinBox.setValue (current.group.values[2])
        self.songOptionsWidget.rouletteSpinBox.setValue (current.group.values[3])
        self.songOptionsWidget.spointsSpinBox.setValue (current.group.values[4])

    @pyqtSlot ("QString")
    def treeView_filter (self, pattern):
        self.filter_unlock_model.setFilterRegExp (pattern)
        self.treeView.sortByColumn (0)
        topindex = self.treeView.model ().index (0, 0, QModelIndex ())
        self.treeView.setCurrentIndex (topindex)

    def _group_update_needed (self, group):
        update = False
        values = [0 for i in range (0, 5)]

        values[0] = self.songOptionsWidget.arcadeSpinBox.value ()
        values[1] = self.songOptionsWidget.clearSpinBox.value ()
        values[2] = self.songOptionsWidget.danceSpinBox.value ()
        values[3] = self.songOptionsWidget.rouletteSpinBox.value ()
        values[4] = self.songOptionsWidget.spointsSpinBox.value ()

        if values != group.values:
            update = True

        return update

    def _group_update (self, group):
        group.values[0] = self.songOptionsWidget.arcadeSpinBox.value ()
        group.values[1] = self.songOptionsWidget.clearSpinBox.value ()
        group.values[2] = self.songOptionsWidget.danceSpinBox.value ()
        group.values[3] = self.songOptionsWidget.rouletteSpinBox.value ()
        group.values[4] = self.songOptionsWidget.spointsSpinBox.value ()

        return

    # Handle cursor change events
    @pyqtSlot ("QModelIndex", "QModelIndex")
    def on_treeView_currentItemChanged (self, current, previous):
        if not current.isValid () and not previous.isValid ():
            # Widget cleared. No previous selection. Ignore
            return
        elif current.isValid () and not previous.isValid ():
            # Update group information and songs if necessary
            group = self.treeWidget.currentItem ().group
            #print group
            if self._group_update_needed (group):
                self._group_update (group)
                group.change_songs ()

        elif previous.isValid () and not self.in_reset:
            # Widget cleared but selection made. Update song
            song = previous.data (Qt.UserRole).toPyObject ().song
            #song = previous.song
            song.name = self.songOptionsWidget.lineEdit_2.text ()
            song.arcade = self.songOptionsWidget.arcadeSpinBox.value ()
            song.clear = self.songOptionsWidget.clearSpinBox.value ()
            song.dance = self.songOptionsWidget.danceSpinBox.value ()
            song.roulette = self.songOptionsWidget.rouletteSpinBox.value ()
            song.song = self.songOptionsWidget.spointsSpinBox.value ()

        if not current.isValid ():
            # Widget cleared. Ignore
            return

        if not self.in_reset:
            song = current.data (Qt.UserRole).toPyObject ().song
            #song = current.song
            self.songOptionsWidget.itemLabel.setText (self.tr ("Song Name:"))
            self.songOptionsWidget.lineEdit_2.setText (song.name)
            self.songOptionsWidget.arcadeSpinBox.setValue (song.arcade)
            self.songOptionsWidget.clearSpinBox.setValue (song.clear)
            self.songOptionsWidget.danceSpinBox.setValue (song.dance)
            self.songOptionsWidget.rouletteSpinBox.setValue (song.roulette)
            self.songOptionsWidget.spointsSpinBox.setValue (song.song)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    locale = QLocale.system ().name ()
    translator = QTranslator ()
    # Import package to obtain package directory
    package_dir = __import__ ("stepmaniaunlock").__path__[0]
    # Translation files located in package
    if translator.load ("stepmaniaunlock_%s" % locale, os.path.join (package_dir, "translations")):
        app.installTranslator (translator)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

