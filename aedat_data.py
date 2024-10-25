# aedat_data.py
from enum import Enum
from typing import Tuple


class CameraType(Enum):
    DVS128 = 1
    DAVIS240 = 2


class CameraParameters:
    def __init__(self, camera_type: CameraType):
        self.camera_type = camera_type
        if camera_type == CameraType.DVS128:
            self.camera_x = 128
            self.camera_y = 128
        elif camera_type == CameraType.DAVIS240:
            self.camera_x = 240
            self.camera_y = 180


class Event:
    def __init__(self, bytes_data: bytes):
        self.bytes = bytes_data

    def get_polarity(self, cam_type: CameraType) -> bool:
        if cam_type == CameraType.DVS128:
            return (self.bytes[3] & 1) == 1
        elif cam_type == CameraType.DAVIS240:
            return ((self.bytes[2] >> 3) & 1) == 1

    def get_timestamp(self) -> int:
        return (int(self.bytes[7]) +
                (int(self.bytes[6]) << 8) +
                (int(self.bytes[5]) << 16) +
                (int(self.bytes[4]) << 24))

    def get_coords(self, cam_type: CameraType) -> Tuple[int, int]:
        if cam_type == CameraType.DVS128:
            return (
                128 - ((self.bytes[3] >> 1) & 0b1111111),
                128 - (self.bytes[2] & 0b1111111)
            )
        elif cam_type == CameraType.DAVIS240:
            return (
                240 - (((self.bytes[1] << 4) & 0b11110000) + ((self.bytes[2] >> 4) & 0b1111)),
                180 - (((self.bytes[0] << 2) & 0b11111100) + ((self.bytes[1] >> 6) & 0b11))
            )


def get_events(end_of_header_index: int, aedat_file: bytes) -> list[Event]:
    EVENT_SIZE = 8
    events = []

    # Skip header and process events
    data = aedat_file[end_of_header_index:]

    # Process events in chunks of EVENT_SIZE
    for i in range(0, len(data), EVENT_SIZE):
        event_bytes = data[i:i + EVENT_SIZE]
        if len(event_bytes) == EVENT_SIZE:
            events.append(Event(event_bytes))

    return events