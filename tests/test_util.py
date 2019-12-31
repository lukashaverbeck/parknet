import sys
from pathlib import Path
sys.path.append(str(Path(sys.path[0]).parent))

import unittest
from util import Singleton


@Singleton
class Something:
    pass


class TestUtil(unittest.TestCase):
    def setUp(self):
        self.something_1 = Something.instance()
        self.something_2 = Something.instance()
        return super().setUp()

    def test_singleton(self):
        self.assertIs(self.something_1, self.something_2)
        
        with self.assertRaises(TypeError):
            Something()


if __name__ == "__name__":
    unittest.main()