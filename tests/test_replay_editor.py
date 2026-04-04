import unittest
from restorer.replay_editor import ReplayEditor

class TestReplayEditor(unittest.TestCase):
    def test_crc_consistency(self):
        editor = ReplayEditor()
        data = b"RocketLeague"
        crc1 = editor.calculate_ue3_crc(data)
        crc2 = editor.calculate_ue3_crc(data)
        self.assertEqual(crc1, crc2)
        self.assertIsInstance(crc1, int)

if __name__ == '__main__':
    unittest.main()
