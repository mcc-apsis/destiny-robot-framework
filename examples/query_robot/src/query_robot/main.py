"""Main entry point for the Query Robot."""

import asyncio
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

from base_robot.client import create_client
from base_robot.polling_runner import PollingRunner
from base_robot.robot_logging import configure_logging
from base_robot.version import read_version
from query_robot.config import get_settings
from query_robot.robot import QueryRobot


def main() -> None:
    """Run the Query Robot."""

    configure_logging()

    settings = get_settings()

    client = create_client(settings)

    robot = QueryRobot(
        robot_version=read_version(Path(__file__).parent),
    )

    runner = PollingRunner(
        client=client,
        robot=robot,
        settings=settings,
    )

    asyncio.run(runner.run())


if __name__ == "__main__":
    main()