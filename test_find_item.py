import unittest
from unittest.mock import patch, Mock
import miniProj

class TestFindItem(unittest.TestCase):

    @patch('miniProj.simpledialog.askstring', return_value="Some Item")
    @patch('miniProj.create_connection')
    @patch('miniProj.messagebox.showinfo')
    @patch('miniProj.messagebox.showerror')
    def test_find_item_success(self, mock_showerror, mock_showinfo, mock_create_connection, mock_askstring):
        # Mocking the database cursor and connection
        mock_cursor = Mock()
        mock_cursor.fetchone.return_value = (6, 'Record', 'Rumors', 'Fleetwood Mac', '1977', 'Pop', 'Available', 15)
        mock_conn = mock_create_connection.return_value
        mock_conn.cursor.return_value = mock_cursor

        miniProj.find_item()

        # Check if the correct SQL query was executed
        mock_cursor.execute.assert_called_once_with("SELECT * FROM Items WHERE title=?", ('Some Item',))
        
        # Check if the success dialog was shown
        mock_showinfo.assert_called_once()
        mock_showerror.assert_not_called()

    @patch('miniProj.simpledialog.askstring', return_value="Nonexistent Item")
    @patch('miniProj.create_connection')
    @patch('miniProj.messagebox.showinfo')
    @patch('miniProj.messagebox.showerror')
    def test_find_item_failure(self, mock_showerror, mock_showinfo, mock_create_connection, mock_askstring):
        # Mocking the database cursor and connection
        mock_cursor = Mock()
        mock_cursor.fetchone.return_value = None
        mock_conn = mock_create_connection.return_value
        mock_conn.cursor.return_value = mock_cursor

        miniProj.find_item()

        # Check if the correct SQL query was executed
        mock_cursor.execute.assert_called_once_with("SELECT * FROM Items WHERE title=?", ('Nonexistent Item',))

        # Check if the error dialog was shown
        mock_showerror.assert_called_once_with("Error", "Item not found!")
        mock_showinfo.assert_not_called()

if __name__ == "__main__":
    unittest.main()
