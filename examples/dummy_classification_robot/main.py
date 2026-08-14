"""Main entry point for the Relevance Robot."""

import asyncio
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from base_robot.batch_runner import BatchRunner
from base_robot.client import create_client
from base_robot.dummy_classification_robot.config import Settings
from base_robot.dummy_classification_robot.robot import ClassificationRobot
from base_robot.robot_logging import configure_logging
from base_robot.version import read_version


def main() -> None:
    """Run the Classification Robot."""
    
    logger.info("Starting Classification Robot")
    configure_logging()

    settings = Settings(
       _env_file=Path(__file__).parent / ".env", # pyright: ignore[reportCallIssue]
    )

    client = create_client(settings)

    robot = ClassificationRobot(
        settings=settings,
        robot_version=read_version(Path(__file__).parent),
    )

    runner = BatchRunner(
        client=client,
        robot=robot,
        settings=settings,
    )

    asyncio.run(runner.run())


if __name__ == "__main__":
    main()