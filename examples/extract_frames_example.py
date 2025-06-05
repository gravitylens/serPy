import sys
import os

# Add the parent directory of the examples folder to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Now import serPy
import serPy

# Read an existing SER file
metadata, frames, timestamps = serPy.read_ser("TestImages/jup.ser")

# Select a subset of frames
selected_frames = frames[10:20]
selected_timestamps = timestamps[10:20] if timestamps else None
metadata["frame_count"] = len(selected_frames)

# Write the new SER file
serPy.write_ser(
    "output.ser",
    metadata,
    selected_frames,
    selected_timestamps
)

# Save a sample frame as PNG
serPy.save_frame_as_png(frames[0], "test.png", metadata["color_id"])
