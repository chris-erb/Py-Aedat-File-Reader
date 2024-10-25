# video.py
import cv2
import numpy as np
from pathlib import Path
import os
from typing import List, Tuple
from aedat_data import Event, CameraParameters
from dataclasses import dataclass


class Colors:
    RED = (0, 0, 255)  # BGR format for OpenCV
    GREEN = (0, 255, 0)
    BLACK = (0, 0, 0)


@dataclass
class VidConfig:
    filename: Path
    window_size: int
    max_frames: int
    exclude_on: bool
    exclude_off: bool
    keep_frames: bool
    omit_video: bool


def create_time_based_video(events: List[Event], config: VidConfig, cam: CameraParameters) -> None:
    frame_tmp_dir = config.filename if config.keep_frames else Path(".frames_tmp")
    video_name = frame_tmp_dir.stem

    # Create and clear temp directory
    frame_tmp_dir.mkdir(exist_ok=True)
    if not config.keep_frames:
        for file in frame_tmp_dir.glob("*"):
            file.unlink()

    # Initialize frame
    frame = np.zeros((cam.camera_y, cam.camera_x, 3), dtype=np.uint8)

    # Get initial timestamp
    if not events:
        raise ValueError("No events exist")

    end_time = events[0].get_timestamp() + config.window_size
    frames_created = 0

    for event in events:
        # Place pixel on frame
        x, y = event.get_coords(cam.camera_type)
        color = Colors.GREEN if event.get_polarity(cam.camera_type) else Colors.RED

        if ((not config.exclude_on and event.get_polarity(cam.camera_type)) or
                (not config.exclude_off and not event.get_polarity(cam.camera_type))):
            frame[y - 1, x - 1] = color

        if event.get_timestamp() > end_time:
            frames_created += 1
            if frames_created == config.max_frames:
                break

            # Save frame
            frame_path = frame_tmp_dir / f"{video_name}_frame{frames_created}.png"
            cv2.imwrite(str(frame_path), frame)

            # Reset frame
            frame.fill(0)
            end_time = event.get_timestamp() + config.window_size

    # Create video if requested
    if not config.omit_video:
        frame_paths = sorted(frame_tmp_dir.glob("*.png"))
        if frame_paths:
            first_frame = cv2.imread(str(frame_paths[0]))
            height, width = first_frame.shape[:2]

            video_path = str(config.filename) + ".avi"
            fourcc = cv2.VideoWriter_fourcc(*'MJPG')
            out = cv2.VideoWriter(video_path, fourcc, 30.0, (width, height))

            for frame_path in frame_paths:
                frame = cv2.imread(str(frame_path))
                out.write(frame)

            out.release()

    # Clean up temp directory if needed
    if not config.keep_frames:
        for file in frame_tmp_dir.glob("*"):
            file.unlink()
        frame_tmp_dir.rmdir()

def create_event_based_video(events: List[Event], config: VidConfig, cam: CameraParameters) -> None:
    frame_tmp_dir = config.filename if config.keep_frames else Path(".frames_tmp")
    video_name = frame_tmp_dir.stem

    # Create and clear temp directory
    frame_tmp_dir.mkdir(exist_ok=True)
    if not config.keep_frames:
        for file in frame_tmp_dir.glob("*"):
            file.unlink()

    # Initialize frame
    frame = np.zeros((cam.camera_y, cam.camera_x, 3), dtype=np.uint8)

    # Check for events
    if not events:
        raise ValueError("No events exist")

    frames_created = 0
    event_count = 0

    for event in events:
        # Place pixel on frame
        x, y = event.get_coords(cam.camera_type)
        color = Colors.GREEN if event.get_polarity(cam.camera_type) else Colors.RED

        if ((not config.exclude_on and event.get_polarity(cam.camera_type)) or
                (not config.exclude_off and not event.get_polarity(cam.camera_type))):
            frame[y - 1, x - 1] = color
            event_count += 1

        if event_count >= config.window_size:
            frames_created += 1
            if frames_created == config.max_frames:
                break

            # Save frame
            frame_path = frame_tmp_dir / f"{video_name}_frame{frames_created}.png"
            cv2.imwrite(str(frame_path), frame)

            # Reset frame and counter
            frame.fill(0)
            event_count = 0

    # Create video if requested
    if not config.omit_video:
        frame_paths = sorted(frame_tmp_dir.glob("*.png"))
        if frame_paths:
            first_frame = cv2.imread(str(frame_paths[0]))
            height, width = first_frame.shape[:2]

            video_path = str(config.filename) + ".avi"
            fourcc = cv2.VideoWriter_fourcc(*'MJPG')
            out = cv2.VideoWriter(video_path, fourcc, 30.0, (width, height))

            for frame_path in frame_paths:
                frame = cv2.imread(str(frame_path))
                out.write(frame)

            out.release()

    # Clean up temp directory if needed
    if not config.keep_frames:
        for file in frame_tmp_dir.glob("*"):
            file.unlink()
        frame_tmp_dir.rmdir()