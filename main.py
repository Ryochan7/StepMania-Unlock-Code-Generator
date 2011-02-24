#!/usr/bin/env python

import os
import sys
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from ui_mainwindow import Ui_MainWindow
from loadsongs_controller import LoadSongsController
from writeunlock_controller import WriteUnlockController
from readunlock_controller import ReadUnlockController

class MainWindow (QMainWindow, Ui_MainWindow):
    def __init__ (self, parent = None):
        super (MainWindow, self).__init__ (parent)
        self.setupUi (self)
        self.connect (self.actionQuit, SIGNAL ("triggered ()"),
            qApp, SLOT ("quit ()"))
        #self.actionQuit.triggered.connect (qApp.quit)
        self.loadsong_thread = None
        self.group_collection = []
        self.songOptionsFrame.hide ()
        self.treeWidget.clear ()
        item = QTreeWidgetItem (["All"])
        itfont = QFont ()
        itfont.setBold (True)
        item.setFont (0, itfont)
        self.treeWidget.addTopLevelItem (item)
        self.all_item = item

        self.treeWidget.sortItems (0, Qt.AscendingOrder)
        self.treeWidget_2.sortItems (0, Qt.AscendingOrder)

    @pyqtSlot ()
    def on_toolButton_clicked (self):
        fileName = QFileDialog.getExistingDirectory (self,
            "Choose StepMania Directory", os.path.dirname (__file__))

        if fileName:
            print fileName
            self.lineEdit.setText (fileName)
            self.loadSongsButton.setEnabled (True)
        print "Automatic connection made"


    @pyqtSlot ()
    def on_loadSongsButton_clicked (self):
        searchfolder = str(self.lineEdit.text ())
        if not searchfolder:
            # No directory selected. Return
            return
        elif not os.path.isdir (os.path.join (searchfolder, "Songs")):
            return

        self.treeWidget.clear ()
        self.treeWidget_2.clear ()

        self.group_collection = []
        controller = LoadSongsController (searchfolder, self.group_collection)
        controller.groupload_notice.connect (self.statusbar.showMessage)
        controller.finished.connect (self.songOptionsFrame.show)
        controller.finished.connect (self.populateTreeWidgets)
        controller.start ()
        self.loadsong_thread = controller

    @pyqtSlot ()
    def populateTreeWidgets (self):
        for i, group in enumerate (self.group_collection):
            item = QTreeWidgetItem ([group.name])
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

        self.loadsong_thread = None
        self.group_collection = []

    @pyqtSlot ()
    def on_cancelButton_clicked (self):
        # self.songOptionsFrame.hide ()
        qApp.quit ()

    @pyqtSlot ()
    def on_resetButton_clicked (self):
        self.treeWidget_2.clearSelection ()
        self.treeWidget.clearSelection ()
        self.treeWidget_2.clear ()

        iterator = QTreeWidgetItemIterator (self.treeWidget)
        while (iterator.value ()):
            iteritem = iterator.value ()
            for song in iteritem.group.songs:
                song.reset ()

            iterator += 1
        self.treeWidget.scrollToTop ()
        topitem = self.treeWidget.topLevelItem (0)
        self.treeWidget.setCurrentItem (topitem)

    @pyqtSlot ()
    def on_saveButton_clicked (self):
        print "Add saving controller"
        searchfolder = str(self.lineEdit.text ())

        print self.treeWidget.currentItem ()
        print self.treeWidget_2.currentItem ()
        groupitem = self.treeWidget.currentItem ()
        songitem = self.treeWidget_2.currentItem ()
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
            print group
            if self._group_update_needed (group):
                self._group_update (group)
                group.change_songs ()

        # Save final data
        controller = WriteUnlockController (searchfolder, self.all_item.group.songs)
        controller.run ()

        qApp.quit ()

    # Handle cursor change events
    @pyqtSlot ("QTreeWidgetItem*", "QTreeWidgetItem*")
    def on_treeWidget_currentItemChanged (self, current, previous):
        print "IN WIDGET 1"
        print current
        print previous
        if not current and not previous:
            # Widget cleared. No previous selection. Ignore
            return

        if previous:
            group = previous.group
            print group
            if self._group_update_needed (group):
                self._group_update (group)
                group.change_songs ()

        print "BEFORE CLEAR"
        self.treeWidget_2.clear ()
        print "AFTER CLEAR"

        if not current:
            # Recheck for current item. Used to follow update group logic
            return

        # Regular group selected. Populate treeWidget with songs from group
        for song in current.group.songs:
            item = QTreeWidgetItem ([song.name])
            item.song = song
            self.treeWidget_2.addTopLevelItem (item)

        self.songOptionsWidget.lineEdit_2.setText (current.group.name)
        self.songOptionsWidget.arcadeSpinBox.setValue (current.group.values[0])
        self.songOptionsWidget.clearSpinBox.setValue (current.group.values[1])
        self.songOptionsWidget.danceSpinBox.setValue (current.group.values[2])
        self.songOptionsWidget.rouletteSpinBox.setValue (current.group.values[3])
        self.songOptionsWidget.spointsSpinBox.setValue (current.group.values[4])

    def _group_update_needed (self, group):
        update = False
        values = [0 for i in range (0, 5)]

        values[0] = self.songOptionsWidget.arcadeSpinBox.value ()
        values[1] = self.songOptionsWidget.clearSpinBox.value ()
        values[2] = self.songOptionsWidget.danceSpinBox.value ()
        values[3] = self.songOptionsWidget.rouletteSpinBox.value ()
        values[4] = self.songOptionsWidget.spointsSpinBox.value ()

        print "CHECK EQUALITY"
        if values != group.values:
            update = True

        print values == group.values

        return update

    def _group_update (self, group):
        group.values[0] = self.songOptionsWidget.arcadeSpinBox.value ()
        group.values[1] = self.songOptionsWidget.clearSpinBox.value ()
        group.values[2] = self.songOptionsWidget.danceSpinBox.value ()
        group.values[3] = self.songOptionsWidget.rouletteSpinBox.value ()
        group.values[4] = self.songOptionsWidget.spointsSpinBox.value ()

        return

    # Handle cursor change events
    @pyqtSlot ("QTreeWidgetItem*", "QTreeWidgetItem*")
    def on_treeWidget_2_currentItemChanged (self, current, previous):
        print "IN WIDGET 2"
        print current
        print previous
        if not current and not previous:
            # Widget cleared. No previous selection. Ignore
            return
        elif current and not previous:
            # Update group information and songs if necessary
            group = self.treeWidget.currentItem ().group
            print group
            if self._group_update_needed (group):
                self._group_update (group)
                group.change_songs ()

        elif previous:
            # Widget cleared but selection made. Update song
            song = previous.song
            song.name = self.songOptionsWidget.lineEdit_2.text ()
            song.arcade = self.songOptionsWidget.arcadeSpinBox.value ()
            song.clear = self.songOptionsWidget.clearSpinBox.value ()
            song.dance = self.songOptionsWidget.danceSpinBox.value ()
            song.roulette = self.songOptionsWidget.rouletteSpinBox.value ()
            song.song = self.songOptionsWidget.spointsSpinBox.value ()

        if not current:
            # Widget cleared. Ignore
            return

        song = current.song
        self.songOptionsWidget.lineEdit_2.setText (song.name)
        self.songOptionsWidget.arcadeSpinBox.setValue (song.arcade)
        self.songOptionsWidget.clearSpinBox.setValue (song.clear)
        self.songOptionsWidget.danceSpinBox.setValue (song.dance)
        self.songOptionsWidget.rouletteSpinBox.setValue (song.roulette)
        self.songOptionsWidget.spointsSpinBox.setValue (song.song)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

