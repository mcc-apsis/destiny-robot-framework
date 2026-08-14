"""Factory for creating DESTINY clients."""

import destiny_sdk

from base_robot.config import RobotConfiguration


def create_client(
    settings: RobotConfiguration,
) -> destiny_sdk.client.Client:
    """Create a configured DESTINY client."""

    return destiny_sdk.client.Client(
        base_url=settings.destiny_repository_url,
        client_id=settings.robot_id,
        secret_key=settings.robot_secret,
    )