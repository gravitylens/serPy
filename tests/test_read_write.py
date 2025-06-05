import sys
import os

# Ensure the package is importable when running tests directly
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import numpy as np
import serPy


def test_write_and_read_ser(tmp_path):
    width, height, nframes = 5, 4, 3
    metadata = {
        "file_id": "LUCAM-RECORDER",
        "lu_id": 1,
        "color_id": 0,
        "little_endian": True,
        "image_width": width,
        "image_height": height,
        "pixel_depth": 8,
        "frame_count": nframes,
        "observer": "Tester",
        "instrument": "TestCam",
        "telescope": "TestScope",
        "date_time": 637738597820000000,
        "date_time_utc": 637738597820000000,
    }
    frames = [np.random.randint(0, 256, (height, width), dtype=np.uint8) for _ in range(nframes)]
    timestamps = [metadata["date_time"] + i for i in range(nframes)]

    ser_file = tmp_path / "temp.ser"
    serPy.write_ser(str(ser_file), metadata, frames, timestamps)

    read_metadata, read_frames, read_timestamps = serPy.read_ser(str(ser_file))

    assert read_metadata == metadata
    assert len(read_frames) == len(frames)
    for orig, loaded in zip(frames, read_frames):
        assert np.array_equal(orig, loaded)
    assert read_timestamps == timestamps
