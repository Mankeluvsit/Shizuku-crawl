from __future__ import annotations

from .config import build_arg_parser, config_from_args
from .pipeline import run_pipeline


def main() -> None:
    parser = build_arg_parser()
    args = parser.parse_args()
    config = config_from_args(args)
    run_pipeline(config)
