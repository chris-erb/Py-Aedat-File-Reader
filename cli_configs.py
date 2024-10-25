# cli_configs.py
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Optional


class CoordMode(Enum):
    NO_COORD = 0
    XY = 1
    PIXEL_NUM = 2


@dataclass
class CsvConfig:
    filename: Path
    include_polarity: bool
    coords: CoordMode
    offset_time: bool

    @classmethod
    def from_args(cls, args):
        filename = Path(args.filename)
        filename = filename.with_suffix('.csv')

        include_polarity = args.include_polarity and not args.exclude_polarity

        if args.coords:
            coords = CoordMode.XY
        elif args.pixel_number:
            coords = CoordMode.PIXEL_NUM
        elif args.no_spatial:
            coords = CoordMode.NO_COORD
        else:
            raise ValueError("Invalid coordinate mode configuration")

        return cls(
            filename=filename,
            include_polarity=include_polarity,
            coords=coords,
            offset_time=args.offset_time
        )


@dataclass
class TimeWindowConfig:
    filename: Path
    include_both_column: bool
    include_pgm: bool
    window_size: int
    max_windows: int
    pgm_scale: int
    pgm_threshold: int

    @classmethod
    def from_args(cls, args):
        filename = Path(args.filename)
        filename = filename.with_suffix('.csv')

        return cls(
            filename=filename,
            include_both_column=args.include_both,
            include_pgm=args.include_pgm,
            window_size=args.window_size,
            max_windows=args.max_windows or float('inf'),
            pgm_scale=args.pgm_scale or 1,
            pgm_threshold=args.pgm_threshold or 0
        )

    def create_csv_header(self) -> str:
        header = ["On", "Off"]

        if self.include_both_column:
            header.append("Both")

        if self.include_pgm:
            header.append("PGM_String")

        return ",".join(header) + "\n"


@dataclass
class VidConfig:
    filename: Path
    window_size: int
    max_frames: int
    exclude_on: bool
    exclude_off: bool
    keep_frames: bool
    omit_video: bool

    @classmethod
    def from_args(cls, args):
        filename = Path(args.filename)
        filename = filename.with_suffix('')

        return cls(
            filename=filename,
            window_size=args.window_size,
            max_frames=args.max_frames or float('inf'),
            exclude_on=args.exclude_on_events,
            exclude_off=args.exclude_off_events,
            keep_frames=args.keep_frames,
            omit_video=args.omit_video
        )