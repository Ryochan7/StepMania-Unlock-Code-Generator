import os
import sys
from time import time
from shutil import copy

# Writes the unlock file and shows a prompt telling the user
# where the unlock file is located
class WriteUnlockController (object):
    def __init__ (self, searchfolder, songs):
        self.searchfolder = searchfolder
        self.songs = songs

    def run (self):
        # Attempt to make a backup copy of the Unlocks.dat file
        datafolder = os.path.join (self.searchfolder, "Data")
        if (os.path.isdir (datafolder)):
            writefile = os.path.join (datafolder, "Unlocks.dat")
            if (os.path.isfile (writefile)):
                backupfile = os.path.join (datafolder, "Unlocks.dat.backup")
                try:
                    copy (writefile, backupfile)
                    print "Backup File: %s" % backupfile
                except (IOError, OSError):
                    print >> sys.stderr, "Permission denied for writing to %s." % backupfile
                    print >> sys.stderr, "No backup file will be created."
        else:
            home = os.path.expanduser ("~")
            writefile = os.path.join (home, "Unlocks.dat")
            if (os.path.isfile (writefile)):
                backupfile = os.path.join (home, "Unlocks.dat.backup")
                try:
                    copy (writefile, backupfile)
                    print "Backup File: %s" % backupfile
                except (IOError, OSError):
                    print >> sys.stderr, "Permission denied for writing to %s." % backupfile
                    print >> sys.stderr, "No backup file will be created."

        # Starts the writing of the Unlocks.dat file
        message = """// Test file for Miryo's new Unlock system.
// Songs/courses are matched by name, not folder name
//
// System modified by curewater
//
// The following methods are implemented:
//
// DP - Dance points, e.g. 2 per perfect, 1 per great, etc.
// AP - Arcade points, like MAX2 arcade
// SP - Song points, like MAX2 Home
// CS - Clear Stages, like 5th Home
// RO - Roulette, unlocked by landing on it in roulette.
//
// To be implemented: Toasty, Clear Extra Stages, Fail Extra Stages.
//
// Courses will be implemented eventually, but not yet.
// Songs are matched by title + subtitle.
//
// Any line not starting with #UNLOCK will be ignored.
//
// Sample lines:
//
// #UNLOCK:xenon:AP=10;
// Song xenon requires 10 arcade points to unlock.
//
// #UNLOCK:the Legend of MAX:RO=3
// Song "the Legend of Max" is in roulette slot 3.
//
// #UNLOCK:PARANOIA SURVIVOR MAX:CS=30,RO=3;
// Song "Paranoia Surivvor MAX" is locked either by clearing
// 30 stages, or by landing on it in roulette slot 3.
//
// #UNLOCK:POP 4:CS=50;
// Course Pop 4 is locked until 50 stages are cleared.
// (Stepmania doesn't distinguish between song and course titles
// yet.
//

"""
        starttime = time ()
        try:
            unlockfile = open (writefile, 'w')
        except IOError:
            print >> sys.stderr, "Permission denied for writing to %s. Exiting program." % writefile
            #self.prompt_text.set_text ("Permission denied for writing to\n%s. Exiting program." % writefile)
            #self.prompt_window.run ()
            return

        unlockfile.write(message)
        for song in self.songs:
            i = 1
            changes = []
            # Find which properties have been changed
            # and place the categories in a temporary list
            for stat in [song.arcade, song.clear, song.dance, song.roulette, song.song]:
                if stat != 0:
                    if i == 1:
                        changes.append ("arcade")
                    elif i == 2:
                        changes.append ("clear")
                    elif i == 3:
                        changes.append ("dance")
                    elif i == 4:
                        changes.append ("roulette")
                    else:
                        changes.append ("song")
                i += 1
            # If any categories exist in the list, write an unlock entry
            # with the categories in the appropriate order
            if changes:
                i = 1
                unlockfile.write ("#UNLOCK:%s:" % song.name_trans)
                for stat_type in changes:
                    if stat_type == "arcade":
                        unlockfile.write ("AP=%s" % song.arcade)
                    elif stat_type == "clear":
                        unlockfile.write ("CS=%s" % song.clear)
                    elif stat_type == "dance":
                        unlockfile.write ("DP=%s" % song.dance)
                    elif stat_type == "roulette":
                        unlockfile.write ("RO=%s" % song.roulette)
                    elif stat_type == "song":
                        unlockfile.write ("SP=%s" % song.song)
                    if i < len (changes):
                        unlockfile.write (",")
                        i += 1
                    else:
                        unlockfile.write (";\n")
        unlockfile.write ('\n')
        unlockfile.close ()
        endtime = time ()
        print "Wrote Unlocks.dat:    %.3f" % (endtime - starttime)
        print "Unlock File: %s" % writefile
        # Set text for final prompt window and show the window
        #self.prompt_text.set_text ("File Unlocks.dat has been written to\n%s" % writefile)
        #self.prompt_window.show ()


