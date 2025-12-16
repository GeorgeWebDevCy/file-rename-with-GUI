import unittest
from pathlib import Path
import sys
import os

# Add parent directory to path to import file_renamer
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from file_renamer import file_name_rule, folder_name_rule

class TestRenamerLogic(unittest.TestCase):
    def test_file_name_rule_title_case(self):
        # Basic title casing
        self.assertEqual(file_name_rule("hello world.txt"), "Hello World.txt")
        self.assertEqual(file_name_rule("HELLO WORLD.txt"), "Hello World.txt")
        self.assertEqual(file_name_rule("mixed CASE name.txt"), "Mixed Case Name.txt")
        
        # Handling numbers and suffixes
        self.assertEqual(file_name_rule("image (1).jpg"), "Image.jpg")
        self.assertEqual(file_name_rule("vacation_photo.PNG"), "Vacation_photo.PNG") # underscores might be treated as part of word by title() depending on implementation, let's check current behavior. 
        # Actually .title() in python splits by non-alphabetical usually. "vacation_photo".title() -> "Vacation_Photo"
        
        # Verify specific behavior of current implementation
        # The current implementation uses: stem.lower().title()
        # "vacation_photo".lower().title() -> "Vacation_Photo"
        self.assertEqual(file_name_rule("vacation_photo.PNG"), "Vacation_Photo.PNG")

    def test_folder_name_rule(self):
        self.assertEqual(folder_name_rule("my folder"), "MY FOLDER")
        self.assertEqual(folder_name_rule("photos (1)"), "PHOTOS")
        self.assertEqual(folder_name_rule("1. my folder"), "1. MY FOLDER")

if __name__ == '__main__':
    unittest.main()
