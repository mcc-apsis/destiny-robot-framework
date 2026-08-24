from pathlib import Path

import destiny_sdk

from cluster_robot.batch import BatchMetadata
from cluster_robot.robot import ClusterRobot


class DummyRobot(ClusterRobot):
    SLURM_SCRIPT = Path(__file__).parent / "slurm.sh"

    def write_input(
        self,
        references: list[destiny_sdk.references.Reference],
        input_file: Path,
    ) -> None:
        input_file.write_text(str(len(references)))

    def parse_output(
        self,
        predictions_file: Path,
        metadata: BatchMetadata,
    ) -> list[destiny_sdk.enhancements.Enhancement]:
        return []