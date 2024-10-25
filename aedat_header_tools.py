# aedat_header_tools.py
from typing import List
from aedat_data import CameraParameters, CameraType


def find_line_in_header(aedat_file: bytes, search: str) -> str:
    try:
        # Read first 524288 bytes (0.5MB) or entire file if smaller
        header_size = min(524288, len(aedat_file))
        header = aedat_file[:header_size]

        # Decode bytes to string and search for line
        contents = header.decode('utf-8', errors='ignore')

        # Debug: Print first few lines of the header
        print("\nDebug - First few lines of header:")
        print('\n'.join(contents.splitlines()[:10]))

        for line in contents.splitlines():
            if search in line:
                print(f"Debug - Found line: {line}")
                return line

        raise ValueError(f"'{search}' was not found in the file")
    except UnicodeDecodeError as e:
        print(f"Debug - Unicode decode error: {str(e)}")
        raise
    except Exception as e:
        print(f"Debug - Unexpected error: {str(e)}")
        raise


def parse_camera_type(aedat_file: bytes) -> CameraParameters:
    try:
        # Print first few lines of the file for debugging
        print("\nDebug - First 500 bytes of file header:")
        header_preview = aedat_file[:500].decode('utf-8', errors='ignore')
        print(header_preview)

        # Try different possible header fields
        hardware_interface = None
        possible_headers = [
            "# HardwareInterface:",
            "# Device Type:",
            "# Camera:",
            "# DVS Type:",
            "# Platform:",
            "# Sensor:"
        ]

        for header in possible_headers:
            try:
                hardware_interface = find_line_in_header(aedat_file, header)
                if hardware_interface:
                    print(f"Debug - Found header line: {header} {hardware_interface}")
                    break
            except:
                continue

        # If no header found, try to determine from filename
        if not hardware_interface:
            if "DVS240" in str(aedat_file):
                print("Debug - Determining camera type from filename")
                return CameraParameters(CameraType.DAVIS240)

        # Rest of the function remains the same
        if hardware_interface:
            hardware_interface = hardware_interface.lower()
            if any(x in hardware_interface for x in ["dvs128", "dvs-128"]):
                return CameraParameters(CameraType.DVS128)
            elif any(x in hardware_interface for x in ["davis240", "dvs240", "davis-240", "dvs-240"]):
                return CameraParameters(CameraType.DAVIS240)

        raise ValueError("Could not determine camera type")

    except Exception as e:
        print(f"Debug - Error parsing camera type: {str(e)}")
        raise ValueError("Could not parse camera type") from e


def parse_camera_type(aedat_file: bytes) -> CameraParameters:
    try:
        # Try different possible header fields
        hardware_interface = None
        possible_headers = [
            "# HardwareInterface:",
            "# Device Type:",
            "# Camera:",
            "# DVS Type:"
        ]

        for header in possible_headers:
            try:
                hardware_interface = find_line_in_header(aedat_file, header)
                if hardware_interface:
                    break
            except:
                continue

        if not hardware_interface:
            raise ValueError("Could not find camera information in header")

        # Convert to lowercase for case-insensitive matching
        hardware_interface = hardware_interface.lower()

        # Check for different camera type variations
        if any(x in hardware_interface for x in ["dvs128", "dvs-128"]):
            return CameraParameters(CameraType.DVS128)
        elif any(x in hardware_interface for x in ["davis240", "dvs240", "davis-240", "dvs-240"]):
            return CameraParameters(CameraType.DAVIS240)

        # If header parsing fails, try checking the file content for camera type
        file_content = aedat_file.decode('utf-8', errors='ignore').lower()
        if "dvs128" in file_content or "dvs-128" in file_content:
            return CameraParameters(CameraType.DVS128)
        elif any(x in file_content for x in ["davis240", "dvs240", "davis-240", "dvs-240"]):
            return CameraParameters(CameraType.DAVIS240)

        # If still no match, print debug info and raise error
        print(f"Debug - Found hardware interface: {hardware_interface}")
        raise ValueError(f"Unrecognized camera type in: {hardware_interface}")

    except Exception as e:
        print(f"Debug - Error parsing camera type: {str(e)}")
        raise ValueError("Could not parse camera type") from e


def find_header_end(aedat_file: bytes) -> int:
    # Search for "#End Of ASCII Header\r\n"
    END_OF_ASCII = b"#End Of ASCII Header\r\n"

    try:
        index = aedat_file.index(END_OF_ASCII)
        return index + len(END_OF_ASCII)
    except ValueError:
        raise ValueError("End of header not found")