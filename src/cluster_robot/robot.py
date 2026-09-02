"""Base class for robots using an HPC cluster."""

import asyncio
import logging
from abc import ABC, abstractmethod
from pathlib import Path
from typing import ClassVar

import destiny_sdk
import httpx

from cluster_robot.batch import BatchMetadata, BatchStore
from cluster_robot.config import ClusterRobotConfiguration
from cluster_robot.slurm import Slurm

logger = logging.getLogger(__name__)

class ClusterRobot(ABC):
    """Base class for cluster-based robots."""

    upload_headers: ClassVar[dict[str, str]] = {
        "Content-Type": "application/jsonl",
        "x-ms-blob-type": "BlockBlob",
    }
    SLURM_SCRIPT: Path

    def __init__(
            self, 
            robot_version: str,
            settings: ClusterRobotConfiguration,
            ):
        self.robot_version = robot_version
        self.settings = settings
        self.workspace = settings.workspace

        self.batch_store = BatchStore(self.workspace)
        self.slurm = Slurm(
            slurm_script=self.SLURM_SCRIPT,
            batch_store=self.batch_store,
        )

    #
    # ---------- Preparation ----------
    #

    async def prepare(
            self,
            batch: destiny_sdk.robots.RobotEnhancementBatch,
        ) -> None:
        """Download references for one batch, prepare the batch and submit a Slurm job."""

        logger.info("Preparing batch %s", batch.id)

        batch_dir = self.batch_store.initialize_batch(batch, self.robot_version)
        logger.info("Initialized batch directory: %s", batch_dir)
        references = await self.download_references(str(batch.reference_storage_url))
        self.write_input(references, self.batch_store.input_file(batch_dir))

        job_id = self.slurm.submit(batch_dir)
        logger.info("Submitted Slurm job %s for batch %s", job_id, batch.id)

        metadata = self.batch_store.read_metadata(batch_dir)
        metadata.slurm_job_id = job_id
        self.batch_store.write_metadata(batch_dir, metadata)

    async def prepare_all(
        self,
        client: destiny_sdk.client.Client,
        robot_id: destiny_sdk.UUID,
        batch_size: int,
    ) -> None:
        """Prepare all currently available enhancement batches."""

        logger.info("Preparing all available enhancement batches.")
        while True:
            batch = client.poll_robot_enhancement_batch(
                robot_id=robot_id,
                limit=batch_size,
                lease=self.settings.batch_lease,
            )

            if batch is None:
                logger.info("No more enhancement batches available.")
                return
           
            await self.prepare(batch)

    #
    # ---------- Waiting for job completion ----------
    #

    async def wait_all(self) -> None:
        """Wait for all submitted Slurm jobs to finish successfully."""


        jobs = [
            self.batch_store.read_metadata(batch_dir)
            for batch_dir in self.batch_store.submitted_batches()
        ]

        if not jobs:
            logger.info("No submitted Slurm jobs to wait for.")
            return

        if self.settings.slurm_api_url is None:
            non_local_jobs = [
                metadata
                for metadata in jobs
                if metadata.slurm_job_id != "local"
            ]

            if non_local_jobs:
                raise RuntimeError(
                    "Cannot wait for Slurm jobs: no Slurm API URL configured."
                )

        headers = {}

        if self.settings.slurm_user:
            headers["X-SLURM-USER-NAME"] = self.settings.slurm_user

        if self.settings.slurm_token:
            headers["X-SLURM-USER-TOKEN"] = self.settings.slurm_token

        wait_tasks = []

        for metadata in jobs:
            job_id = metadata.slurm_job_id

            if job_id is None:
                continue

            if job_id == "local":
                logger.info(
                    "Local job for batch %s already completed.",
                    metadata.batch_id,
                )
                continue

            if self.settings.slurm_api_url is None:
                raise RuntimeError(
                    "Cannot wait for Slurm jobs: no Slurm API URL configured."
                )

            wait_tasks.append(
                self.slurm.wait_for_job(
                    job_id=job_id,
                    api_url=self.settings.slurm_api_url,
                    poll_interval=self.settings.wait_poll_interval,
                    headers=headers,
                )
            )

        await asyncio.gather(*wait_tasks)

    #
    # ---------- Upload ----------
    #

    async def upload_all_finished(
            self,
            client: destiny_sdk.client.Client,
            ) -> None:
        """Upload all finished batches in the workspace."""

        uploaded_batches = 0

        for batch_dir in self.batch_store.finished_batches():
            metadata: BatchMetadata | None = None
            try:
                metadata = self.batch_store.read_metadata(batch_dir)

                logger.info("Uploading finished batch %s",metadata.batch_id,)

                enhancements = self.parse_output(
                    self.batch_store.predictions_file(batch_dir),
                    metadata,
                )

                await self.upload_enhancements(
                    enhancements,
                    metadata.result_storage_url,
                )

                # notify DESTINY that the batch has been processed
                client.send_robot_enhancement_batch_result(
                        destiny_sdk.robots.RobotEnhancementBatchResult(
                            request_id=metadata.batch_id,
                        )
                    )
                # store locally that the batch has been uploaded, so we don't try to upload it again
                self.batch_store.mark_uploaded(batch_dir)

                uploaded_batches += 1

                logger.info(
                    "Successfully uploaded and acknowledged batch %s",
                    metadata.batch_id,
                )

            except Exception:
                logger.exception(
                    "Failed to upload batch %s",
                    metadata.batch_id if metadata else batch_dir.name,
                )
            
        logger.info("Finished uploading %d batch(es).", uploaded_batches)

    #
    # ---------- Common helpers ----------
    #

    async def download_references(
        self, 
        reference_storage_url: str
    ) -> list[destiny_sdk.references.Reference]:
        """Download and parse references from storage URL."""
        references = []
        async with (
            httpx.AsyncClient() as client,
            client.stream("GET", reference_storage_url) as response,
        ):
            response.raise_for_status()
            async for line in response.aiter_lines():
                reference = destiny_sdk.references.Reference.model_validate_json(
                    line
                )
                references.append(reference)
        return references


    @abstractmethod
    def write_input(
        self,
        references: list[destiny_sdk.references.Reference],
        input_file: Path,
    ) -> None:
        """Write the classifier input for the cluster."""


    @abstractmethod
    def parse_output(
        self,
        predictions_file: Path,
        metadata: BatchMetadata,
    ) -> list[destiny_sdk.enhancements.Enhancement]:
        """Read model output and build DESTINY enhancements."""

    async def upload_enhancements(
        self,
        enhancements: list[destiny_sdk.enhancements.Enhancement],
        result_storage_url: str,
    ) -> None:
        """Upload enhancements to the given storage URL."""
        
        file_content = b""
        for enhancement in enhancements:
            file_content += (enhancement.to_jsonl() + "\n").encode("utf-8")

        async with httpx.AsyncClient() as client:
            response = await client.put(
                result_storage_url,
                content=file_content,
                headers=self.upload_headers,
            )
            response.raise_for_status()