
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from file_renamer import file_name_rule, folder_name_rule

print(f"Original: 'hello world.txt', Result: '{file_name_rule('hello world.txt')}'")
print(f"Original: 'mixed CASE name.txt', Result: '{file_name_rule('mixed CASE name.txt')}'")
print(f"Original: 'image (1).jpg', Result: '{file_name_rule('image (1).jpg')}'")
print(f"Original: 'my folder', Result: '{folder_name_rule('my folder')}'")
print(f"Original: 'photos (1)', Result: '{folder_name_rule('photos (1)')}'")
