import os
import sys
import math
from time import time
from PyQt4.QtCore import QThread, pyqtSignal
from PyQt4.QtGui import QApplication
from stepmaniaunlock.extraclasses import Song, SongGroup

class LoadSongsController (QThread):
    groupload_notice = pyqtSignal (str)
    smfileread_complete = pyqtSignal (int)

    def __init__ (self, searchfolder, group_collect, parent=None):
        super (LoadSongsController, self).__init__ (parent)
        self.group_collection = group_collect
        self.group_collection.append (SongGroup ("All"))
        self.searchfolder = searchfolder
        self.num_files = 0
        self.smread_complete = 0
        self.exiting = False

    def run (self):
        starttime = time ()
        file_collection = self._filewalk ()
        self._read_files (file_collection)
        endtime = time ()
        print "LoadSongsController: %.3f" % (endtime - starttime)

    def _read_files (self, file_collection):
        for group_name, song_files in file_collection:
            self.groupload_notice.emit ("Loading Group: %s" % group_name)
            entries = self._smfile_read (song_files)
            if len (entries) == 0:
                continue

            entries.sort (key=lambda x: x.name.lower ())
            newgroup = SongGroup (group_name, entries)
            self.group_collection.append (newgroup)
            self.group_collection[0].songs.extend (newgroup.songs)

        self.groupload_notice.emit ("")
        print "Files read: %d" % len (self.group_collection[0].songs)

    def _filewalk (self):
        file_collection = []
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

                num_songs = len (songpaths)
                if num_songs == 0:
                    continue
                else:
                    self.num_files += len (songpaths)

                file_collection.append ([folders, songpaths])

        return file_collection

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
                self.smread_complete += 1
                progress = (self.smread_complete / float (self.num_files)) * 100
                progress = int (math.floor (progress))
                self.smfileread_complete.emit (progress)
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
                self.smread_complete += 1
                progress = (self.smread_complete / float (self.num_files)) * 100
                progress = int (math.floor (progress))
                self.smfileread_complete.emit (progress)
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

            self.smread_complete += 1
            progress = (self.smread_complete / float (self.num_files)) * 100
            progress = int (math.floor (progress))
            self.smfileread_complete.emit (progress)
        return entries


    def __del__ (self):
        self.exiting = True
        self.wait ()

