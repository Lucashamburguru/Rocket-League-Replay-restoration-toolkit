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

    def test_find_property(self):
        editor = ReplayEditor()
        editor.load('RLreplaysUnedited/oldreplay.replay')
        pos = editor.find_property("PlayerName")
        self.assertNotEqual(pos, -1)
        # Check if the bytes at pos match "PlayerName"
        self.assertEqual(editor.data[pos+4:pos+4+10], b"PlayerName")

    def test_update_int(self):
        import struct
        editor = ReplayEditor()
        editor.load('RLreplaysUnedited/oldreplay.replay')
        # Find initial Goals (should be 2 in our sample)
        success = editor.update_int_property("Goals", 99)
        self.assertTrue(success)
        # Re-find to verify
        pos = editor.find_property("Goals")
        type_pos = editor.data.find(b"IntProperty\x00", pos)
        val = struct.unpack('<I', editor.data[type_pos+20:type_pos+24])[0]
        self.assertEqual(val, 99)

if __name__ == '__main__':
    unittest.main()
