class Song:
    def __init__ (self, name, name_trans, arcade=0, clear=0, dance=0, roulette=0, song=0):
        #print name
        self.name = name.decode ('utf8', 'replace')
        self.name_trans = name_trans.decode ('utf8', 'replace')
        self.arcade = arcade
        self.clear = clear
        self.dance = dance
        self.roulette = roulette
        self.song = song
        self._defaults = [arcade, clear, dance, roulette, song]

    def reset (self):
        self.arcade, self.clear, self.dance, self.roulette, self.song = self._defaults

    # An unlock code has been found for this song. Update the values and defaults for this
    # Song object according to the unlock code values
    def unlock_values (self, changes):
        self._defaults = changes
        self.arcade, self.clear, self.dance, self.roulette, self.song = self._defaults

    def __str__ (self):
        return u'%s' % self.name

class SongGroup:
    changes = []
    def __init__ (self, name, songs=None):
        self.name = name.decode ('utf8', 'replace')
        if songs:
            self.songs = songs
        else:
            self.songs = []

        self.values = [0, 0, 0, 0, 0]
        self._defaults = [0, 0, 0, 0, 0]

    def reset (self):
        self.values = self._defaults
        for song in self.songs:
            song.reset ()

    # A SongGroup object values have been changed. Update the values of all the songs
    # listed in the SongGroup
    def change_songs (self):
        for song in self.songs:
            song.arcade, song.clear, song.dance, song.roulette, song.song = self.values

    def __str__ (self):
        return u"%s" % self.name


