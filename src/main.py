import os
import argparse
from rich import print

from process import process_command
from config import EDITION_SOURCES

EDITIONS = list(EDITION_SOURCES.keys())

parser = argparse.ArgumentParser(
    description="Generate MEI headers from a CSV file and merge them into MEI files.",
    usage="ricercarmei --data <path_to_csv> [--mei-files <path_to_mei_files>] [--edition <edition_choice>]"
)
parser.add_argument(
    "--data",
    type=str,
    help="Path to the CSV file containing the data for MEI headers.",
    required=True
)
parser.add_argument(
    "--mei-files",
    type=str,
    help="Path to the directory containing MEI files.",
)
parser.add_argument(
    "--edition",
    choices=EDITIONS,
    help="The edition type to use for the generated headers.",
    default="printed"
)

def main():
    args = parser.parse_args()

    files = os.listdir(args.mei_files) if args.mei_files else []
    file_count = 0
    for file in files:
        if file.endswith(".mei"): file_count += 1
    print(f"Found {file_count} MEI files in the directory: {args.mei_files}" if args.mei_files else "No MEI files provided.")

    if not os.path.exists(args.data):
        raise FileNotFoundError(f"The specified data file does not exist: {args.data}")

    process_command(files=args.mei_files, data=args.data, edition_type=args.edition)

if __name__ == "__main__":
    main()
