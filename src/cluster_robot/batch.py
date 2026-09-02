"""Manage batch directories for cluster robots.
- Create batch directories.
- Read/write metadata.json.
- Know where the input and output files live.
- Discover finished batches.
- Mark uploads as completed.
"""

from __future__ import annotations

from pathlib import Path

import destiny_sdk
from pydantic import BaseModel


class BatchMetadata(BaseModel):
    batch_id: destiny_sdk.UUID
    reference_storage_url: str
    result_storage_url: str
    robot_version: str
    slurm_job_id: str | None = None


class BatchStore:
    """Manage batch directories and metadata."""

    INPUT_DIR = "input"
    OUTPUT_DIR = "output"
    LOG_DIR = "logs"

    INPUT_FILENAME = "references.jsonl"
    PREDICTIONS_FILENAME = "predictions.jsonl"
    METADATA_FILENAME = "metadata.json"
    UPLOADED_FILENAME = "uploaded"

    def __init__(self, workspace: Path):
        self.workspace = workspace
        self.workspace.mkdir(parents=True, exist_ok=True)

    def initialize_batch(
        self,
        batch: destiny_sdk.robots.RobotEnhancementBatch,
        robot_version: str,
    ) -> Path:
        """Create a new batch directory."""

        batch_dir = self.batch_dir(batch.id)

        (batch_dir / self.INPUT_DIR).mkdir(parents=True, exist_ok=True)
        (batch_dir / self.OUTPUT_DIR).mkdir(exist_ok=True)
        (batch_dir / self.LOG_DIR).mkdir(exist_ok=True)

        metadata = BatchMetadata(
            batch_id=batch.id,
            reference_storage_url=str(batch.reference_storage_url),
            result_storage_url=str(batch.result_storage_url),
            robot_version=robot_version,
        )

        self.write_metadata(batch_dir, metadata)
        

        return batch_dir

    def submitted_batches(self) -> list[Path]:
        """Return batches with a submitted Slurm job that have not been uploaded."""

        return sorted(
            batch_dir
            for batch_dir in self.workspace.iterdir()
            if (
                batch_dir.is_dir()
                and self.metadata_file(batch_dir).exists()
                and not self.uploaded_file(batch_dir).exists()
                and self.read_metadata(batch_dir).slurm_job_id is not None
            )
        )

    def finished_batches(self) -> list[Path]:
        """Return batches with finished predictions."""

        return sorted(
            batch_dir
            for batch_dir in self.workspace.iterdir()
            if (
                batch_dir.is_dir()
                and self.predictions_file(batch_dir).exists()
                and not self.uploaded_file(batch_dir).exists()
            )
        )

    def read_metadata(self, batch_dir: Path) -> BatchMetadata:
        """Read batch metadata."""

        return BatchMetadata.model_validate_json(
            self.metadata_file(batch_dir).read_text()
        )

    def write_metadata(
        self,
        batch_dir: Path,
        metadata: BatchMetadata,
    ) -> None:
        """Write metadata.json."""

        self.metadata_file(batch_dir).write_text(
            metadata.model_dump_json(indent=2)
        )

    def mark_uploaded(self, batch_dir: Path) -> None:
        """Mark a batch as uploaded."""

        (batch_dir / self.UPLOADED_FILENAME).touch()

    def input_file(self, batch_dir: Path) -> Path:
        return batch_dir / self.INPUT_DIR / self.INPUT_FILENAME

    def predictions_file(self, batch_dir: Path) -> Path:
        return batch_dir / self.OUTPUT_DIR / self.PREDICTIONS_FILENAME

    def metadata_file(self, batch_dir: Path) -> Path:
        return batch_dir / self.METADATA_FILENAME

    def uploaded_file(self, batch_dir: Path) -> Path:
        return batch_dir / self.UPLOADED_FILENAME

    def batch_dir(self, batch_id: destiny_sdk.UUID) -> Path:
        return self.workspace / str(batch_id)

    def log_dir(self, batch_dir: Path) -> Path:
        return batch_dir / self.LOG_DIR

    def stdout_file(self, batch_dir: Path) -> Path:
        return self.log_dir(batch_dir) / "slurm.out"

    def stderr_file(self, batch_dir: Path) -> Path:
        return self.log_dir(batch_dir) / "slurm.err"