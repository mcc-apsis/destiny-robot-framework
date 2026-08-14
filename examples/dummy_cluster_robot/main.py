import asyncio
from pathlib import Path

from cluster_robot.config import ClusterRobotConfiguration
from cluster_robot.main import run_robot
from cluster_robot.version import read_version

from .robot import DummyRobot

settings = ClusterRobotConfiguration(
    _env_file=Path(__file__).parent / ".env", # pyright: ignore[reportCallIssue]
)
settings.workspace = (Path(__file__).parent / settings.workspace).resolve()

if __name__ == "__main__":
    asyncio.run(
        run_robot(
            robot_cls=DummyRobot,
            robot_version=read_version(Path(__file__).parent),
            settings=settings,
        )
    )