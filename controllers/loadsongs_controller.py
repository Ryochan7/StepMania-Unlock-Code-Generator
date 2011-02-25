import os
import sys
from time import time
from PyQt4.QtCore import QThread, pyqtSignal
from PyQt4.QtGui import QApplication
from extraclasses import Song, SongGroup

class LoadSongsController (QThread):
    groupload_notice = pyqtSignal (str)

    def __init__ (self, searchfolder, group_collect, parent=None):
        super (LoadSongsController, self).__init__ (parent)
        self.group_collection = group_collect
        self.group_collection.append (SongGroup ("All"))
        self.searchfolder = searchfolder
        self.exiting = False

    def run (self):
        starttime = time ()
        self._filewalk ()
        endtime = time ()
        print "LoadSongsController: %.3f" % (endtime - starttime)

    def _filewalk (self):
        searchfolder = os.path.join (self.searchfolder, "Songs")
        if not os.path.isdir (searchfolder):
            return
        root = os.listdir (searchfolder)
        root.sort (key=lambda x: x.lower())
        for folders in root:
            group_folder = os.path.join (searchfolder, folders)
            if os.path.isdir (group_folder):
                song_folders = os.listdir (group_folder)
                songpaths = []
                for song_folder in song_folders:
                    if os.path.isdir (os.path.join(group_folder, song_folder)):
                        song_files = os.listdir (os.path.join(group_folder, song_folder))
                        song_files.sort (key=lambda x: x.lower())
                        song_files.reverse ()
                        for song_file in song_files:
                            if song_file[-3:].lower () == ".sm":
                                filepath = os.path.join (group_folder, song_folder, song_file)
                                songpaths.append (filepath)
                                #print "Sm: %s" % song_file
                                break
                            if song_file[-4:].lower () == ".dwi":
                                filepath = os.path.join (group_folder, song_folder, song_file)
                                songpaths.append (filepath)
                                #print "Dwi: %s" % song_file
                                break

                if len (songpaths) == 0:
                    continue

                self.groupload_notice.emit ("Loading Group: %s" % folders)
                entries = self._smfile_read (songpaths)
                if len (entries) == 0:
                    continue
                entries.sort (key=lambda x: x.name.lower ())
                newgroup = SongGroup (folders, entries)
                self.group_collection.append (newgroup)
                self.group_collection[0].songs.extend (newgroup.songs)

        self.groupload_notice.emit ("")
        print "Files read: %d" % len (self.group_collection[0].songs)

    # Reads in the .sm/.dwi files within a group folder, makes the
    # required Song objects, and returns the list of Song objects
    def _smfile_read (self, songfiles):
        entries = []
        for filepath in songfiles:
            # Double check to make sure the file exists prior to reading it.
            # Especially necessary when trying to read files with Unicode names
            # under Windows
            if not os.path.exists (filepath):
                print >> sys.stderr, "%s could not be read. Skipping." % filepath
                continue

            temp_filepath = filepath.lower ()
            if temp_filepath[-4:] == ".dwi":
                filetype = ".dwi"
            else:
                filetype = ".sm"
            title = ""
            subtitle = ""
            title_trans = ""
            subtitle_trans = ""

            try:
                smfile = open (filepath, 'r')
            except IOError:
                print >> sys.stderr, "%s could not be read. Skipping." % filepath
                continue
            readline = smfile.readline ()
            while readline:
                if filetype == ".dwi" and title:
                    break
                elif filetype == ".sm" and title and subtitle and title_trans and subtitle_trans:
                    break

                if readline.find ("#TITLE:") != -1:
                    parsedline = readline.strip().split("#TITLE:")[1]
                    parsedline = parsedline.rstrip (';')
                    if filetype == ".dwi":
                        title = ' '.join (parsedline.split())
                    else:
                        title = parsedline.strip ()
                elif filetype != ".sm":
                    readline = smfile.readline ()
                    continue
                elif readline.find ("#SUBTITLE:") != -1:
                    parsedline = readline.strip().split("#SUBTITLE:")[1]
                    parsedline = parsedline.rstrip (';')
                    subtitle = parsedline.strip ()
                elif readline.find ("#TITLETRANSLIT:") != -1:
                    parsedline = readline.strip().split("#TITLETRANSLIT:")[1]
                    parsedline = parsedline.rstrip (';')
                    title_trans = parsedline.strip ()
                elif readline.find ("#SUBTITLETRANSLIT:") != -1:
                    parsedline = readline.strip().split("#SUBTITLETRANSLIT:")[1]
                    parsedline = parsedline.rstrip (';')
                    subtitle_trans = parsedline.strip ()
                readline = smfile.readline ()
            smfile.close ()

            if not title:
                continue
            if not title_trans:
                title_trans = title
            if not subtitle_trans:
                subtitle_trans = subtitle

            if not subtitle and not subtitle_trans:
                temp_song = Song (title, title_trans)
            elif not subtitle:
                temp_song = Song (title, "%s %s" % (title_trans, subtitle_trans))
            elif not subtitle_trans:
                temp_song = Song ("%s %s" % (title, subtitle), title_trans)
            else:
                temp_song = Song ("%s %s" % (title, subtitle), "%s %s" % (title_trans, subtitle_trans))
            entries.append (temp_song)
        return entries


    def __del__ (self):
        self.exiting = True
        self.wait ()


if __name__ == "__main__":
    app = QApplication(sys.argv)

    group_collection = []
    controller = LoadSongsController (os.getcwd (), group_collection)
    controller.finished.connect (app.quit)

    controller.start ()
    controller.wait ()
    print group_collection
    for group in group_collection:
        print group
        print
        for song in group.songs:
            print song

    app.exec_ ()

