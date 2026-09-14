"""Shared entry point for cluster-based robots."""

import argparse
import logging

from cluster_robot.client import create_client
from cluster_robot.config import ClusterRobotConfiguration
from cluster_robot.robot import ClusterRobot

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)

async def run_robot(
    robot_cls: type[ClusterRobot],
    robot_version: str,
    settings: ClusterRobotConfiguration,
) -> None:
    """Run a cluster-based robot."""

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "command",
        choices=["prepare", "wait", "upload"],
    )
    
    args = parser.parse_args()

    client = create_client(settings)

    robot = robot_cls(
        robot_version=robot_version,
        settings=settings,
    )

    if args.command == "prepare":
        await robot.prepare_all(
            client=client,
            robot_id=settings.robot_id,
            batch_size=settings.batch_size,
        )

    elif args.command == "wait":
        await robot.wait_all()
    
    else:
        await robot.upload_all_finished(client)