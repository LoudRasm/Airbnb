"""Compatibility entry point; uses the shared workbook-based data check."""
import sys
from check_data import main

if __name__ == "__main__":
    raise SystemExit(main(["--part", "calendar", *sys.argv[1:]]))
