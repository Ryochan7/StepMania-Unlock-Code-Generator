import unittest
from stepmaniaunlock.extraclasses import Song

class SongTest (unittest.TestCase):
    def setUp (self):
        self.song1 = Song ("ABC", "abc")

    def test_unlock_values (self):
        new_values = [1, 2, 3, 4, 5]

        self.song1.unlock_values (new_values)
        new_list = [self.song1.arcade, self.song1.clear, self.song1.dance, self.song1.roulette, self.song1.song]
        for i, item in enumerate (new_list):
            self.assertEqual (item, new_values[i])

    def test_reset (self):
        self.song1.arcade = 500
        self.song1.clear = 10
        self.song1.dance = 5
        self.song1.roulette = 10
        self.song1.song = 10000
        defaults = list (self.song1._defaults)
        self.song1.reset ()

        new_list = [self.song1.arcade, self.song1.clear, self.song1.dance, self.song1.roulette, self.song1.song]
        for i, item in enumerate (new_list):
            self.assertEqual (item, defaults[i])


if __name__ == "__main__":
    unittest.main ()

