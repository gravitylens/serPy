import sys
import os

# Add the parent directory of the examples folder to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Now import serPy
import serPy
import numpy as np

metadata = {
    "file_id": "LUCAM-RECORDER",
    "lu_id": 12345,
    "color_id": 0,
    "little_endian": True,
    "image_width": 640,
    "image_height": 480,
    "pixel_depth": 8,
    "frame_count": 10,
    "observer": "Astronomer",
    "instrument": "ASI290MC",
    "telescope": "Celestron",
    "date_time": 637738597820000000,
    "date_time_utc": 637738597820000000,
}

frames = [np.random.randint(0, 256, (480, 640), dtype=np.uint8) for _ in range(10)]
serPy.write_ser("output.ser", metadata, frames)
