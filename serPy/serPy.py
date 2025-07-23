import struct
import numpy as np
from datetime import datetime, timedelta
from PIL import Image
import cv2
import logging

logger = logging.getLogger(__name__)

# Mapping of color_id to OpenCV Bayer conversion codes
BAYER_CONVERSION_CODES = {
    8: cv2.COLOR_BAYER_RG2RGB,
    9: cv2.COLOR_BAYER_GR2RGB,
    10: cv2.COLOR_BAYER_GB2RGB,
    11: cv2.COLOR_BAYER_BG2RGB,
    # Other Bayer patterns (e.g., CYMG) are less commonly supported in OpenCV
    # These require custom processing if needed
}

def save_frame_as_png(frame, output_path, color_id, align_rgb=True):
    """
    Saves a debayered and optionally RGB-aligned frame as a PNG file.

    Parameters:
        frame (np.ndarray): Frame array (2D Bayer-encoded or grayscale).
        output_path (str): File path for the output PNG.
        color_id (int): Color format ID, determines the Bayer pattern.
        align_rgb (bool): Whether to perform RGB alignment.
    """
    if color_id in BAYER_CONVERSION_CODES:
        # Perform debayering using OpenCV
        debayered_frame = cv2.cvtColor(frame, BAYER_CONVERSION_CODES[color_id])
    elif color_id == 0:  # MONO
        # No debayering needed, use the frame directly
        debayered_frame = frame
    else:
        raise ValueError(f"Unsupported or unknown color_id: {color_id}")

    if align_rgb and debayered_frame.ndim == 3:  # Only align if RGB
        # Split channels
        b, g, r = cv2.split(debayered_frame)

        # Align each channel to green (reference)
        criteria = (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 50, 0.001)
        warp_mode = cv2.MOTION_TRANSLATION

        # Align Blue to Green
        warp_matrix = np.eye(2, 3, dtype=np.float32)
        try:
            _, warp_matrix = cv2.findTransformECC(g, b, warp_matrix, warp_mode, criteria)
            b_aligned = cv2.warpAffine(
                b,
                warp_matrix,
                (g.shape[1], g.shape[0]),
                flags=cv2.INTER_LINEAR + cv2.WARP_INVERSE_MAP,
            )
        except cv2.error as e:
            logger.warning("Blue channel alignment failed: %s", e)
            b_aligned = b

        # Align Red to Green
        warp_matrix = np.eye(2, 3, dtype=np.float32)
        try:
            _, warp_matrix = cv2.findTransformECC(g, r, warp_matrix, warp_mode, criteria)
            r_aligned = cv2.warpAffine(
                r,
                warp_matrix,
                (g.shape[1], g.shape[0]),
                flags=cv2.INTER_LINEAR + cv2.WARP_INVERSE_MAP,
            )
        except cv2.error as e:
            logger.warning("Red channel alignment failed: %s", e)
            r_aligned = r

        # Merge aligned channels back into an RGB image
        debayered_frame = cv2.merge([b_aligned, g, r_aligned])

    # Convert NumPy array to a PIL Image
    if debayered_frame.ndim == 2:  # Grayscale
        image = Image.fromarray(debayered_frame)
    elif debayered_frame.ndim == 3:  # RGB
        image = Image.fromarray(debayered_frame, "RGB")
    else:
        raise ValueError("Frame dimensions are invalid for PNG conversion.")

    # Save the image as PNG
    image.save(output_path)
    print(f"Frame saved as {output_path}")
    
def ser_timestamp_to_datetime(timestamp):
    """
    Converts an SER timestamp (8-byte integer) to a readable date-time string.

    Parameters:
        timestamp (int): SER timestamp representing 100-nanosecond intervals since midnight, Jan 1, 0001.

    Returns:
        str: Readable date-time string in ISO format.
    """
    # Define the epoch for SER timestamps (midnight, January 1, 0001)
    ser_epoch = datetime(1, 1, 1)

    # Convert the timestamp to a timedelta (each unit is 100 nanoseconds)
    delta = timedelta(microseconds=timestamp / 10)

    # Add the timedelta to the epoch to get the actual date-time
    readable_datetime = ser_epoch + delta

    # Return as a readable string
    return readable_datetime.isoformat()

def write_ser(output_path, metadata, frames, timestamps=None):
    """
    Writes an SER file with the given metadata, frames, and optional timestamps.

    Parameters:
        output_path (str): Path to the output SER file.
        metadata (dict): Metadata including file_id, dimensions, pixel depth, etc.
        frames (list of np.ndarray): List of 2D frame arrays to write.
        timestamps (list of int, optional): List of timestamps to write. Must match the number of frames.

    Returns:
        None
    """
    # Define the header structure based on the specification
    header_format = "<14sIIIIIII40s40s40s8s8s"

    # Validate metadata
    if "file_id" not in metadata or metadata["file_id"] != "LUCAM-RECORDER":
        raise ValueError("Invalid metadata: file_id must be 'LUCAM-RECORDER'.")

    # Validate frame dimensions
    frame_height = metadata["image_height"]
    frame_width = metadata["image_width"]
    pixel_depth = metadata["pixel_depth"]
    frame_count = metadata["frame_count"]

    if len(frames) != frame_count:
        raise ValueError("Number of frames does not match frame_count in metadata.")

    # Determine the data type for writing frame bytes
    dtype = np.uint8 if pixel_depth == 8 else np.uint16

    # Open the output file
    with open(output_path, "wb") as ser_file:
        # Pack and write the header
        header = struct.pack(
            header_format,
            metadata["file_id"].encode("utf-8"),
            metadata["lu_id"],
            metadata["color_id"],
            int(metadata["little_endian"]),
            frame_width,
            frame_height,
            pixel_depth,
            frame_count,
            metadata["observer"].encode("utf-8"),
            metadata["instrument"].encode("utf-8"),
            metadata["telescope"].encode("utf-8"),
            struct.pack("<Q", metadata["date_time"]),
            struct.pack("<Q", metadata["date_time_utc"]),
        )
        ser_file.write(header)

        # Write the frames
        for frame in frames:
            if frame.shape != (frame_height, frame_width):
                raise ValueError(f"Frame dimensions {frame.shape} do not match metadata ({frame_height}, {frame_width}).")
            ser_file.write(frame.astype(dtype).tobytes())

        # Write the timestamps (if provided)
        if timestamps:
            if len(timestamps) != frame_count:
                raise ValueError("Number of timestamps does not match frame_count.")
            for timestamp in timestamps:
                ser_file.write(struct.pack("<Q", timestamp))

    print(f"SER file written successfully to {output_path}")

def read_ser(input_path):
    """
    Reads an SER file with the updated header structure.

    Parameters:
        input_path (str): Path to the input SER file.

    Returns:
        dict: Metadata including width, height, pixel depth, frame count, and more.
        list: List of frames (as NumPy arrays).
        list: List of timestamps (if available, otherwise None).
    """
    with open(input_path, "rb") as ser_file:
        # Define the header structure based on the specification
        header_format = "<14sIIIIIII40s40s40s8s8s"
        header_size = struct.calcsize(header_format)

        # Read the header
        header = ser_file.read(header_size)

        # Unpack the header
        (
            file_id,
            lu_id,
            color_id,
            little_endian,
            image_width,
            image_height,
            pixel_depth,
            frame_count,
            observer,
            instrument,
            telescope,
            date_time,
            date_time_utc
        ) = struct.unpack(header_format, header)

        # Validate the file
        if file_id != b"LUCAM-RECORDER":
            raise ValueError("Invalid SER file: Incorrect File ID.")

        # Prepare metadata
        # Helper to decode fixed-width string fields without trailing null bytes
        def _decode_field(value: bytes) -> str:
            return value.decode("utf-8").rstrip("\x00").strip()

        metadata = {
            "file_id": _decode_field(file_id),
            "lu_id": lu_id,
            "color_id": color_id,
            "little_endian": bool(little_endian),
            "image_width": image_width,
            "image_height": image_height,
            "pixel_depth": pixel_depth,
            "frame_count": frame_count,
            "observer": _decode_field(observer),
            "instrument": _decode_field(instrument),
            "telescope": _decode_field(telescope),
            "date_time": struct.unpack("<Q", date_time)[0],
            "date_time_utc": struct.unpack("<Q", date_time_utc)[0],
        }

        # Determine pixel data type
        dtype = np.uint8 if pixel_depth == 8 else np.uint16

        # Calculate frame size
        frame_size = image_width * image_height * (pixel_depth // 8)

        # Read frames
        frames = []
        for _ in range(frame_count):
            frame_data = ser_file.read(frame_size)
            if not frame_data:
                raise ValueError("Unexpected end of file while reading frames.")
            frame = np.frombuffer(frame_data, dtype=dtype)
            frames.append(frame.reshape((image_height, image_width)))

        # Read timestamps (if available)
        timestamps = []
        remaining_data = ser_file.read()
        if len(remaining_data) >= 8 * frame_count:
            timestamps = [
                struct.unpack_from("<Q", remaining_data, i * 8)[0]
                for i in range(frame_count)
            ]
        else:
            timestamps = None

    return metadata, frames, timestamps
