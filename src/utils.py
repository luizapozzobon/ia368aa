"""Project-wide utility functions."""
from argparse import ArgumentParser
from pathlib import Path


def default_parser() -> ArgumentParser:
    """Return a default parser that accepts an assets and outputs directory."""
    parser = ArgumentParser()
    parser.add_argument(
        "--assets_dir",
        default="assets",
        type=Path,
        help="Directory to look for required assets.",
    )
    parser.add_argument(
        "--outputs_dir",
        default="outputs",
        type=Path,
        help="Directory to export processed data.",
    )
    return parser
