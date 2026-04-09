from __future__ import annotations

from .config import build_arg_parser, config_from_args
from .pipeline import run_pipeline
from .webui import serve_webui


def main() -> None:
    parser = build_arg_parser()
    args = parser.parse_args()
    config = config_from_args(args)
    if config.webui:
        serve_webui(config)
        return
    run_pipeline(config)
