import unittest
from unittest.mock import patch
from src.main import App
import os

class TestApp(unittest.TestCase):

    # Setup override to init mock data
    def setUp(self):
        conf = {
            'HOST': 'http://test.com',
            'TOKEN': 'this_is_a_token',
            'T_MAX': '80',
            'T_MIN': '20',
            'DATABASE': 'test_db'
        }
        with patch.dict(os.environ, conf):
            self.app = App()

    def test_sum(self):
        self.assertEqual(sum([1, 2, 3]), 6, "Should be 6")

if __name__ == '__main__':
    unittest.main()
