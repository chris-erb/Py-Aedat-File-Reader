# time_window_csv.py
from dataclasses import dataclass
from pathlib import Path
import numpy as np
from typing import List, Optional  # Added Optional here

from aedat_data import Event, CameraParameters
from cli_configs import TimeWindowConfig

class Downres:
    def __init__(self, size_x: int, size_y: int, scale: int, threshold: int):
        self.pixels = [0] * (size_x // scale * size_y // scale)
        self.size_x = size_x
        self.size_y = size_y
        self.size_x_downscaled = size_x // scale
        self.size_y_downscaled = size_y // scale
        self.scale = scale
        self.threshold = threshold

    def reset(self):
        self.pixels.fill(0)

    def get_pixel(self, x: int, y: int) -> Optional[int]:
        if 0 < x <= self.size_x and 0 < y <= self.size_y:
            return self.pixels[(y - 1) // self.scale, (x - 1) // self.scale]
        return None

    def increment_pixel(self, x: int, y: int):
        if 0 < x <= self.size_x and 0 < y <= self.size_y:
            self.pixels[(y - 1) // self.scale, (x - 1) // self.scale] += 1
        else:
            raise ValueError("Index out of bounds")

    def to_pgm(self) -> str:
        header = f"P2\n{self.size_x_downscaled} {self.size_y_downscaled}\n1\n"

        # Convert pixels to binary based on threshold
        binary = (self.pixels >= self.threshold).astype(int)

        # Convert to string with proper formatting
        rows = []
        for row in binary:
            rows.append(" ".join(map(str, row)))

        return header + "\n".join(rows) + "\n"


def create_time_window_csv(events: List[Event], config: TimeWindowConfig, cam: CameraParameters):
    with open(config.filename, 'w') as f:
        # Write header
        f.write(config.create_csv_header())

        if not events:
            raise ValueError("No events exist")

        end_time = events[0].get_timestamp() + config.window_size

        on_count = 0
        off_count = 0
        windows_created = 0

        # Initialize downscaled PGM image
        downres = Downres(
            cam.camera_x,
            cam.camera_y,
            config.pgm_scale,
            config.pgm_threshold
        )

        for event in events:
            if event.get_timestamp() > end_time:
                # Write current window data
                line = f"{on_count},{off_count}"

                if config.include_both_column:
                    line += f",{on_count + off_count}"

                if config.include_pgm:
                    pgm_str = downres.to_pgm().replace('\n', '-')