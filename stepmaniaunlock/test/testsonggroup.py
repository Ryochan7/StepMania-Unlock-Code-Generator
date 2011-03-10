import unittest
from stepmaniaunlock.extraclasses import Song, SongGroup

class SongGroupTest (unittest.TestCase):
    def setUp (self):
        self.song1 = Song ("song1", "song1")
        self.song2 = Song ("song2", "song2")
        self.song3 = Song ("song3", "song3")
        song_list = [self.song1, self.song2, self.song3]
        self.group = SongGroup ("All", song_list)

    def test_changes_songs (self):
        self.assertEqual (len (self.group.values), 5)
        self.group.values[0] = 5
        self.group.values[1] = 2
        self.group.values[2] = 8
        self.group.values[3] = 9000
        self.group.values[4] = 0

        self.group.change_songs ()
        for song in self.group.songs:
            self.assertEqual (song.arcade, self.group.values[0])
            self.assertEqual (song.clear, self.group.values[1])
            self.assertEqual (song.dance, self.group.values[2])
            self.assertEqual (song.roulette, self.group.values[3])
            self.assertEqual (song.song, self.group.values[4])

    def test_reset (self):
        defaults = list (self.group._defaults)
        self.assertEqual (len (defaults), 5)
        self.group.values[0] = 5
        self.group.values[1] = 10000
        self.group.reset ()
        self.assertEqual (self.group.values[0], defaults[0])
        self.assertEqual (self.group.values[1], defaults[1])
        for song in self.group.songs:
            self.assertEqual (song.arcade, 0)
            self.assertEqual (song.clear, 0)
            self.assertEqual (song.dance, 0)
            self.assertEqual (song.roulette, 0)
            self.assertEqual (song.song, 0)

if __name__ == "__main__":
    unittest.main ()

