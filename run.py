import os
import sys
import subprocess
from typing import List, Optional


def get_aedat_files() -> List[str]:
    input_dir = "Input"
    return [f for f in os.listdir(input_dir) if f.endswith('.aedat')]


def select_file() -> Optional[str]:
    files = get_aedat_files()

    if not files:
        print("No .aedat files found in Input directory!")
        return None

    print("\nAvailable files:")
    for i, file in enumerate(files, 1):
        print(f"{i}. {file}")

    while True:
        try:
            choice = input("\nSelect file number (or press Enter for first file): ").strip()
            if choice == "":
                # Return just the filename, not the full path
                return files[0]

            index = int(choice) - 1
            if 0 <= index < len(files):
                # Return just the filename, not the full path
                return files[index]
            print("Invalid selection. Please try again.")
        except ValueError:
            print("Please enter a valid number.")


def main():
    selected_file = select_file()
    if not selected_file:
        sys.exit(1)

    # Construct the input path correctly
    input_file = os.path.join("Input", selected_file)
    print(f"\nProcessing: {input_file}")

    # Get the absolute path
    abs_input_file = os.path.abspath(input_file)

    args = ['python', 'main.py', abs_input_file] + sys.argv[1:]
    subprocess.run(args)


if __name__ == "__main__":
    main()