import unittest
from stepmaniaunlock.test.testsong import SongTest
from stepmaniaunlock.test.testsonggroup import SongGroupTest

if __name__ == "__main__":
    suite = unittest.TestLoader ().loadTestsFromTestCase (SongTest)
    suite2 = unittest.TestLoader ().loadTestsFromTestCase (SongGroupTest)
    suite.addTest (suite2)
    unittest.TextTestRunner (verbosity=2).run (suite)

