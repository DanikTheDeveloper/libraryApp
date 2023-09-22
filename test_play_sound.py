import unittest
import os
from miniProj import play_sound, IS_WINDOWS

class TestPlaySound(unittest.TestCase):

    @unittest.skipIf(not IS_WINDOWS, "Skipping this test on non-Windows platforms")
    def test_play_sound_windows(self):
        # For now, we can just make sure it doesn't raise an exception.
        try:
            play_sound()
        except Exception as e:
            self.fail(f"play_sound() raised {type(e)} unexpectedly!")
    
    @unittest.skipIf(IS_WINDOWS, "Skipping this test on Windows platforms")
    def test_play_sound_non_windows(self):
        # Mock the print function and verify it gets called correctly.
        with unittest.mock.patch('builtins.print') as mocked_print:
            play_sound()
            mocked_print.assert_called_with("Sound playback is not supported on this platform.")

if __name__ == '__main__':
    unittest.main()
