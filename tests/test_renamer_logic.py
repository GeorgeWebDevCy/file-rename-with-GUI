import os
import sys
import unittest

# Add parent directory to path to import file_renamer
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from file_renamer import file_name_rule, folder_name_rule

class TestRenamerLogic(unittest.TestCase):
    def test_file_name_rule_capitalizes_only_first_character(self):
        self.assertEqual(file_name_rule("hello world.txt"), "Hello world.txt")
        self.assertEqual(file_name_rule("HELLO WORLD.txt"), "Hello world.txt")
        self.assertEqual(file_name_rule("mixed CASE name.txt"), "Mixed case name.txt")
        self.assertEqual(file_name_rule("image (1).jpg"), "Image.jpg")
        self.assertEqual(file_name_rule("vacation_photo.PNG"), "Vacation_photo.PNG")

    def test_folder_name_rule(self):
        self.assertEqual(folder_name_rule("my folder"), "MY FOLDER")
        self.assertEqual(folder_name_rule("photos (1)"), "PHOTOS")
        self.assertEqual(folder_name_rule("1. my folder"), "1. MY FOLDER")

if __name__ == '__main__':
    unittest.main()
