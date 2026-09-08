#!/usr/bin/env python3
"""Explicit, staged prose compression. No network calls without --provider."""
import argparse
from pathlib import Path
from .compress import compress_file, backup_for


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("filepath", type=Path)
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--candidate", type=Path, help="Agent-reviewed UTF-8 candidate; no provider call")
    source.add_argument("--provider", choices=["claude"], help="Explicitly send the source to Claude")
    args = parser.parse_args()
    try:
        success = compress_file(args.filepath, candidate=args.candidate, provider=args.provider)
        if not success:
            parser.exit(2, "Compression rejected; source unchanged.\n")
        print(f"Compressed: {args.filepath}\nBackup: {backup_for(args.filepath)}")
        print("Structural checks passed; semantic preservation requires reviewing the diff.")
    except KeyboardInterrupt:
        parser.exit(130, "Interrupted.\n")
    except Exception as exc:
        parser.exit(1, f"Compression failed: {exc}\n")


if __name__ == "__main__":
    main()
