from enum import StrEnum
from pathlib import Path

from pydantic import Field

from base_robot.config import RobotConfiguration


class Environment(StrEnum):
    LOCAL = "local"
    DEVELOPMENT = "development"
    STAGING = "staging"
    TEST = "test"


class ClusterRobotConfiguration(RobotConfiguration):
    """Settings shared by all cluster-based robots."""

    workspace: Path = Field(
        default=Path("./workspace"),
        description="Directory for batches and intermediate files.",
    )

    batch_lease: str = Field(
        default="P1DT12H",
        description=(
            "Duration to lease enhancement batches from DESTINY "
            "in ISO 8601 format (e.g. PT6H or P1D)."
        ),
    )