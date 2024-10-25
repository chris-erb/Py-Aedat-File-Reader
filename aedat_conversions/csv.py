# aedat_conversions/csv.py
from typing import List
from aedat_data import Event, CameraParameters
from cli_configs import CsvConfig, CoordMode


def create_csv(events: List[Event], config: CsvConfig, cam: CameraParameters):
    with open(config.filename, 'w') as f:
        # Write header
        header = ["Timestamp"]

        if config.include_polarity:
            header.append("Polarity")

        if config.coords == CoordMode.XY:
            header.extend(["X", "Y"])
        elif config.coords == CoordMode.PIXEL_NUM:
            header.append("PixelNumber")

        f.write(",".join(header) + "\n")

        # Write events
        for event in events:
            timestamp = event.get_timestamp()
            if config.offset_time and events:
                timestamp -= events[0].get_timestamp()

            line = [str(timestamp)]

            if config.include_polarity:
                polarity = "1" if event.get_polarity(cam.camera_type) else "0"
                line.append(polarity)

            if config.coords != CoordMode.NO_COORD:
                x, y = event.get_coords(cam.camera_type)
                if config.coords == CoordMode.XY:
                    line.extend([str(x), str(y)])
                else:  # PIXEL_NUM
                    pixel_num = (y - 1) * cam.camera_x + (x - 1)
                    line.append(str(pixel_num))

            f.write(",".join(line) + "\n")