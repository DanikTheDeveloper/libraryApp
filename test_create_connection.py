# test_create_connection.py
import unittest
from miniProj import create_connection

class TestCreateConnection(unittest.TestCase):

    def test_create_connection(self):
        # For now, we'll just check that it doesn't raise an exception and returns something.
        conn = create_connection()
        self.assertIsNotNone(conn)

if __name__ == '__main__':
    unittest.main()
