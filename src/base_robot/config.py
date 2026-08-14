"""API config parsing and model."""

from enum import StrEnum

from destiny_sdk import UUID
from pydantic import Field, HttpUrl
from pydantic_settings import BaseSettings, SettingsConfigDict


class Environment(StrEnum):
    """
    Environment that the robot is running in.
    
    **Allowed values**:
    - `local`: The robot is running locally
    - `development`: The robot is running in development
    - `staging`: The robot is running in staging
    - `test`: The robot is running as a test fixture for the repository
    """

    LOCAL = "local"
    DEVELOPMENT = "development"
    STAGING = "staging"
    TEST = "test"

class RobotConfiguration(BaseSettings):
    """Settings model for polling robot."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    robot_secret: str = Field(
        description="Secret needed for communicating with destiny repo.",
    )
    robot_id: UUID = Field(
        description="Client id needed for communicating with destiny repository.",
    )

    destiny_repository_url: HttpUrl

    env: Environment = Field(
        default=Environment.STAGING,
        description="The environment the robot is deployed in.",
    )

class PollingRobotSettings(RobotConfiguration):
    poll_interval_seconds: int = Field(
        default=30,
        description=("How often to poll for new robot enhancement batches (seconds)"),
    )

    batch_size: int = Field(
        default=2,
        description=("The number of references to include per enhancement batch"),
    )