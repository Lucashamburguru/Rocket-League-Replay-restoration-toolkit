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

    def test_update_str_shift(self):
        editor = ReplayEditor()
        editor.load('RLreplaysUnedited/oldreplay.replay')
        original_size = len(editor.data)
        
        # Change "Prince ShitterShindig" (22 chars) to "Gemini" (7 chars)
        # We'll use occurrence 4 which we know is Prince
        success = editor.update_str_property("PlayerName", "Gemini", occurrence=4)
        
        assert success is True
        assert len(editor.data) == original_size - 15
        assert b"Gemini\x00" in editor.data
        
        # Re-load and verify it's NOT the first occurrence that was changed
        # (The first occurrence in oldreplay is "Prince ShitterShindig" too? 
        # No, let's just verify Gemini is at SOME position)
        assert editor.data.count(b"Gemini\x00") == 1

    def test_save(self):
        import os
        import struct
        editor = ReplayEditor()
        editor.load('RLreplaysUnedited/oldreplay.replay')
        
        temp_path = 'Test_Out/test_save.replay'
        os.makedirs('Test_Out', exist_ok=True)
        
        # Modify something
        editor.update_int_property("Goals", 123)
        editor.save(temp_path)
        
        # Load the saved file
        editor2 = ReplayEditor()
        editor2.load(temp_path)
        
        # Verify modification
        pos = editor2.find_property("Goals")
        type_pos = editor2.data.find(b"IntProperty\x00", pos)
        val = struct.unpack('<I', editor2.data[type_pos+20:type_pos+24])[0]
        self.assertEqual(val, 123)
        
        # Verify CRCs
        # Header CRC at offset 4
        h_data = editor2.data[8:8+editor2.header_size]
        h_crc = editor2.calculate_ue3_crc(h_data)
        saved_h_crc = struct.unpack('<I', editor2.data[4:8])[0]
        self.assertEqual(h_crc, saved_h_crc)
        
        # Body CRC
        body_prefix_pos = 8 + editor2.header_size
        body_size = struct.unpack('<I', editor2.data[body_prefix_pos:body_prefix_pos+4])[0]
        body_data = editor2.data[body_prefix_pos+8 : body_prefix_pos+8+body_size]
        body_crc = editor2.calculate_ue3_crc(body_data)
        saved_body_crc = struct.unpack('<I', editor2.data[body_prefix_pos+4:body_prefix_pos+8])[0]
        self.assertEqual(body_crc, saved_body_crc)
        
        if os.path.exists(temp_path):
            os.remove(temp_path)

if __name__ == '__main__':
    unittest.main()
