# PlanetaryImaging

---

### **Functions in This Project**

#### **`read_ser(input_path)`**
Reads an SER file and extracts its metadata, frames, and optional timestamps.

- **Parameters**:
  - `input_path` (str): Path to the `.ser` file to be read.
- **Returns**:
  - `metadata` (dict): Contains metadata such as image dimensions, pixel depth, frame count, observer, and instrument details.
  - `frames` (list of NumPy arrays): A list of 2D arrays representing individual frames in the `.ser` file.
  - `timestamps` (list of int or None): A list of timestamps corresponding to each frame, or `None` if no timestamps are available.
- **Usage**:
  ```python
  metadata, frames, timestamps = read_ser("example.ser")
  ```

---

#### **`write_ser(output_path, metadata, frames, timestamps=None)`**
Writes an SER file using the provided metadata, frames, and optional timestamps.

- **Parameters**:
  - `output_path` (str): Path where the `.ser` file will be saved.
  - `metadata` (dict): Metadata describing the `.ser` file, including dimensions, pixel depth, and more.
  - `frames` (list of NumPy arrays): A list of 2D arrays representing the frames to be saved.
  - `timestamps` (list of int, optional): Optional timestamps for each frame.
- **Returns**:
  - None
- **Usage**:
  ```python
  write_ser("output.ser", metadata, frames, timestamps)
  ```

---

#### **`save_frame_as_png(frame, output_path, color_id, align_rgb=True)`**
Saves a single frame as a PNG image with optional RGB channel alignment.

- **Parameters**:
  - `frame` (np.ndarray): A 2D Bayer-encoded or grayscale image frame.
  - `output_path` (str): Path where the PNG file will be saved.
  - `color_id` (int): The SER color identifier describing the Bayer pattern.
  - `align_rgb` (bool, optional): Align Red and Blue channels to Green. Defaults to `True`.
- **Returns**:
  - None
- **Usage**:
  ```python
  save_frame_as_png(frame, "frame_output.png", color_id=8, align_rgb=False)
  ```

---

#### **`ser_timestamp_to_datetime(timestamp)`**
Converts an SER timestamp (8-byte integer) into a readable date-time string.

- **Parameters**:
  - `timestamp` (int): An SER timestamp, representing 100-nanosecond intervals since midnight, January 1, 0001.
- **Returns**:
  - `str`: A readable date-time string in ISO 8601 format.
- **Usage**:
  ```python
  readable_time = ser_timestamp_to_datetime(637738597820000000)
  ```

---

These functions work together to:
1. Read `.ser` files.
2. Extract and manipulate frames and metadata.
3. Save frames as PNG images.
4. Convert timestamps to human-readable formats.
5. Write `.ser` files with the desired frames, metadata, and timestamps.

See `examples/extract_frames_example.py` for a walkthrough of selecting a
subset of frames from an existing SER file and saving them to a new file.

---

### **Installing Requirements and Running Tests**

1. Install the project dependencies:
   ```bash
   pip install -r requirements.txt
   ```
   Using `opencv-python-headless` instead of `opencv-python` avoids needing
   system libraries such as `libGL1`:
   ```bash
   pip install opencv-python-headless
   ```

2. Run the tests with [pytest](https://pytest.org):
   ```bash
   pytest
   ```

