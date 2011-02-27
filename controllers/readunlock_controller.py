import os
import sys
from time import time

class ReadUnlockController (object):

    def __init__ (self, searchfolder, songs):
        self.searchfolder = searchfolder
        self.songs = songs

    # Reads the unlock codes from the Unlocks.dat file
    def run (self):
        starttime = time ()
        readfile = None
        datafolder = os.path.join (self.searchfolder, "Data")
        if (os.path.isdir (datafolder)):
            readfile = os.path.join (datafolder, "Unlocks.dat")
        else:
            home = os.path.expanduser ("~")
            readfile = os.path.join (home, "Unlocks.dat")

        if not os.path.isfile (readfile):
            print >> sys.stderr, "File \"%s\" does not exist or could not be read." % readfile
            return

        try:
            unlockfile = open (readfile, 'r')
        except (IOError, OSError):
            print >> sys.stderr, "File \"%s\" could not be read." % unlockfile
            return

        print "Read File: %s" % unlockfile.name
        readline = unlockfile.readline ()
        temp = [song.name_trans for song in self.songs]
        full_temp = list (self.songs)

        # Read in the unlock codes, check that the songs listed exist,
        # and change the Song objects with the values in the unlock code
        while readline:
            changes = [0, 0, 0, 0, 0]
            readline = readline.strip ()
            if not readline:
                readline = unlockfile.readline ()
                continue
            elif readline.startswith ("//"):
                readline = unlockfile.readline ()
                continue
            elif readline.find ("#UNLOCK:") == -1:
                readline = unlockfile.readline ()
                continue

            parsedline = readline.split ("#UNLOCK:", 1)[1]
            parsedline = parsedline.strip ()
            title, stats = parsedline.rsplit (':', 1)
            stats = stats.rstrip (';')
            stat_types = stats.split (',')
            for stat in stat_types:
                #print stat
                if stat[0:3] == "AP=":
                    changes[0] = int(stat.lstrip("AP="))
                elif stat[0:3] == "CS=":
                    changes[1] = int(stat.lstrip("CS="))
                elif stat[0:3] == "DP=":
                    changes[2] = int(stat.lstrip("DP="))
                elif stat[0:3] == "RO=":
                    changes[3] = int(stat.lstrip("RO="))
                elif stat[0:3] == "SP=":
                    changes[4] = int(stat.lstrip("SP="))

            try:
                index = temp.index (title)
                current_song = full_temp[index]
                current_song.unlock_values (changes)
                temp.pop (index)
                full_temp.pop (index)
            except ValueError:
                print >> sys.stderr, "Song \"%s\" is not in your Songs folder." % title

            readline = unlockfile.readline()

        endtime = time ()
        print "Read Unlocks.dat: %.3f" % (endtime - starttime)
        return

