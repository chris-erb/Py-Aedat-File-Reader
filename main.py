# main.py
import argparse
from pathlib import Path
import time
import sys

from aedat_data import get_events
from aedat_header_tools import find_header_end, parse_camera_type
from cli_configs import CsvConfig, TimeWindowConfig, VidConfig
from aedat_conversions.csv import create_csv
from aedat_conversions.time_window_csv import create_time_window_csv
from aedat_conversions.video import create_event_based_video, create_time_based_video


def setup_directories():
    # Create input and output directories if they don't exist
    project_dir = Path(__file__).parent
    input_dir = project_dir / "Input"
    output_dir = project_dir / "Output"

    # Create output subdirectories
    output_dirs = {
        'csv': output_dir / 'csv',
        'video': output_dir / 'video',
        'time_window': output_dir / 'time_window'
    }

    # Create directories if they don't exist
    input_dir.mkdir(exist_ok=True)
    for dir_path in output_dirs.values():
        dir_path.mkdir(parents=True, exist_ok=True)

    return input_dir, output_dirs


def setup_argparse():
    parser = argparse.ArgumentParser(description='AEDAT file converter')

    # Input file argument
    parser.add_argument('filename', type=Path, help='Input AEDAT file (from Input directory)')

    # Mode selection group
    mode_group = parser.add_mutually_exclusive_group(required=True)
    mode_group.add_argument('--csv', action='store_true', help='Create CSV output')
    mode_group.add_argument('--video', action='store_true', help='Create video output')
    mode_group.add_argument('--time-window', action='store_true', help='Create time window CSV')

    # CSV conversion arguments
    csv_group = parser.add_argument_group('CSV conversion options')
    polarity_group = csv_group.add_mutually_exclusive_group()
    polarity_group.add_argument('--include-polarity', action='store_true',
                                help='Include polarity information in CSV')
    polarity_group.add_argument('--exclude-polarity', action='store_true',
                                help='Exclude polarity information from CSV')

    coord_group = csv_group.add_mutually_exclusive_group()
    coord_group.add_argument('--coords', action='store_true',
                             help='Include X,Y coordinates in CSV')
    coord_group.add_argument('--pixel-number', action='store_true',
                             help='Include pixel number instead of coordinates')
    coord_group.add_argument('--no-spatial', action='store_true',
                             help='Exclude spatial information from CSV')

    parser.add_argument('--offset-time', action='store_true',
                        help='Offset timestamps to start from zero')

    # Video reconstruction method group
    video_group = parser.add_argument_group('Video reconstruction options')
    recon_group = video_group.add_mutually_exclusive_group()
    recon_group.add_argument('--time_based', action='store_true',
                             help='Reconstruct frames based on a fixed time window')
    recon_group.add_argument('--event_based', action='store_true',
                             help='Reconstruct frames based on a fixed number of events')

    # Time window and video shared arguments
    window_group = parser.add_argument_group('Window options')
    window_group.add_argument('--window-size', type=int,
                              help='Size of the time/event window')
    window_group.add_argument('--max-windows', type=int,
                              help='Maximum number of windows to process')
    window_group.add_argument('--max-frames', type=int,
                              help='Maximum number of frames to generate (video only)')

    # Time window specific arguments
    time_window_group = parser.add_argument_group('Time window specific options')
    time_window_group.add_argument('--include-both', action='store_true',
                                   help='Include sum of ON and OFF events')
    time_window_group.add_argument('--include-pgm', action='store_true',
                                   help='Include PGM string in output')
    time_window_group.add_argument('--pgm-scale', type=int,
                                   help='Scale factor for PGM output')
    time_window_group.add_argument('--pgm-threshold', type=int,
                                   help='Threshold for PGM output')

    # Video specific arguments
    video_options = parser.add_argument_group('Video specific options')
    video_options.add_argument('--exclude-on-events', action='store_true',
                               help='Exclude ON events from video')
    video_options.add_argument('--exclude-off-events', action='store_true',
                               help='Exclude OFF events from video')
    video_options.add_argument('--keep-frames', action='store_true',
                               help='Keep individual frames after video creation')
    video_options.add_argument('--omit-video', action='store_true',
                               help='Generate frames but do not create video')

    return parser


def process_file(input_file: Path, config, cam, events, mode: str):
    start_time = time.time()

    try:
        if mode == 'csv':
            create_csv(events, config, cam)
        elif mode == 'video':
            if hasattr(config, 'time_based') and config.time_based:
                create_time_based_video(events, config, cam)
            else:
                create_event_based_video(events, config, cam)
        elif mode == 'time_window':
            create_time_window_csv(events, config, cam)

        elapsed = time.time() - start_time
        print(f"Export time: {elapsed:.2f} seconds")

    except Exception as e:
        print(f"Error processing {input_file.name}: {str(e)}")
        return False

    return True


def main():
    # Setup directories
    input_dir, output_dirs = setup_directories()

    # Parse arguments
    parser = setup_argparse()
    args = parser.parse_args()

    try:
        # Resolve input file path
        input_file = input_dir / args.filename
        if not input_file.exists():
            print(f"Input file not found: {input_file}")
            sys.exit(1)

        print(f"Processing {input_file.name}...")

        # Read and parse input file
        with open(input_file, 'rb') as f:
            aedat_file = f.read()

        cam = parse_camera_type(aedat_file)
        header_end = find_header_end(aedat_file)
        events = get_events(header_end, aedat_file)

        # Process based on mode
        if args.csv:
            config = CsvConfig.from_args(args)
            config.filename = output_dirs['csv'] / f"{input_file.stem}.csv"
            success = process_file(input_file, config, cam, events, 'csv')

            if success:
                print(f"CSV file created: {config.filename}")
            else:
                print("Failed to create CSV file")
                sys.exit(1)

        elif args.video:
            if not (args.time_based or args.event_based):
                print("Error: Must specify either --time_based or --event_based for video mode")
                sys.exit(1)

            if not args.window_size:
                print("Error: --window-size is required for video mode")
                sys.exit(1)

            config = VidConfig.from_args(args)
            config.filename = output_dirs['video'] / input_file.stem
            success = process_file(input_file, config, cam, events, 'video')

            if success:
                if not args.omit_video:
                    print(f"Video file created: {config.filename}.avi")
                if args.keep_frames:
                    print(f"Frames preserved in: {config.filename}")
            else:
                print("Failed to create video")
                sys.exit(1)

        elif args.time_window:
            if not args.window_size:
                print("Error: --window-size is required for time window mode")
                sys.exit(1)

            config = TimeWindowConfig.from_args(args)
            config.filename = output_dirs['time_window'] / f"{input_file.stem}_window.csv"
            success = process_file(input_file, config, cam, events, 'time_window')

            if success:
                print(f"Time window CSV file created: {config.filename}")
            else:
                print("Failed to create time window CSV file")
                sys.exit(1)

        else:
            print("Error: No conversion mode specified. Use --csv, --video, or --time-window")
            sys.exit(1)

    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()