import os
import sys

current_file_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_file_dir)
sys.path.append(parent_dir)

from threema.threemaapi import ThreemaAdminClient

client = ThreemaAdminClient()
changes = client.findNormalizations()

print("Found changes: ", changes)
