"""Logging utilities for DESTINY robots."""

import logging


def configure_logging(level: int = logging.INFO) -> None:
    """Configure logging for a robot."""

    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )