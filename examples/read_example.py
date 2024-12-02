import sys
import os

# Add the parent directory of the examples folder to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Now import serPy
import serPy


metadata, frames, timestamps = serPy.read_ser("TestImages/jup.ser")
print("Metadata:", metadata)
print("First frame shape:", frames[0].shape)
