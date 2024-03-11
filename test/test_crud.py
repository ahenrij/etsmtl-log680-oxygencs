import unittest
from unittest.mock import patch
from src.main import App
from src.crud import Table, Crud

class TestCrud(unittest.TestCase):
    def setUp(self):
        self.crud = Crud()

    @patch('psycopg2.connect')
    def test_connect(self, mock_connect):
        self.crud.connect()
        mock_connect.assert_called_once()

    @patch('psycopg2.connect')
    def test_insert_metric(self, mock_connect):
        # Setup a mock connection and cursor
        mock_conn = mock_connect.return_value
        mock_cursor = mock_conn.cursor.return_value

        # Define what the execute method should return
        mock_cursor.execute.return_value = True

        # Test insert_metric
        self.crud.connect() 
        self.crud.insert_metric(Table.HVAC_EVENTS, '2024-03-11T12:00:00Z', '25')
        
        # Ensure the cursor execute method was called once
        mock_cursor.execute.assert_called_once()

        # Ensure commit was called to save changes
        mock_conn.commit.assert_called_once()


if __name__ == '__main__':
    unittest.main()