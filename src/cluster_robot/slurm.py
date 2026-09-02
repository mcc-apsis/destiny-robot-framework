"""Wrapper around Slurm job submission."""

import asyncio
import logging
import shutil
import subprocess
from pathlib import Path

import httpx

from cluster_robot.batch import BatchStore

logger = logging.getLogger(__name__)

SLURM_API_VERSION = "v0.0.43"

class Slurm:
    """Submit jobs to a Slurm cluster."""

    def __init__(
            self, 
            slurm_script: Path,
            batch_store: BatchStore,
    ):
        self.slurm_script = slurm_script
        self.batch_store = batch_store

    def submit(self, batch_dir: Path) -> str:
        """Submit a Slurm job.

        Parameters
        ----------
        batch_dir
            Directory containing the batch input and metadata.

        Returns
        -------
        str
            Slurm job ID.
        """
        stdout_file = self.batch_store.stdout_file(batch_dir)
        stderr_file = self.batch_store.stderr_file(batch_dir)

        if not self.slurm_script.exists():
            raise FileNotFoundError(self.slurm_script)

        if shutil.which("sbatch") is None:
            # local execution for testing
            logger.info(
                "No 'sbatch' found. Running Slurm script %s locally.",
                 self.slurm_script.name,
                )
            subprocess.run(
                [
                    "bash",
                    str(self.slurm_script),
                    str(batch_dir),
                ],
                check=True,
            )
            return "10001"  # dummy job ID for local execution

        else:
            result = subprocess.run(
                [
                    "sbatch",
                    f"--output={stdout_file}",
                    f"--error={stderr_file}",
                    str(self.slurm_script),
                    str(batch_dir),
                ],
                check=True,
                capture_output=True,
                text=True,
            )

            # stdout: "Submitted batch job 123456"
            job_id = result.stdout.strip().split()[-1]
            return job_id

    async def wait_for_job(
        self,
        job_id: str,
        api_url: str,
        poll_interval: int,
        headers: dict[str, str] | None = None,
    ) -> None:
        """Wait until a Slurm job completes successfully."""

        if job_id == "local":
            logger.info("Local job already completed.")
            return

        url = (
            f"{api_url.rstrip('/')}"
            f"/slurm/{SLURM_API_VERSION}/job/{job_id}"
        )

        async with httpx.AsyncClient() as client:
            while True:
                response = await client.get(url, headers=headers)
                response.raise_for_status()

                data = response.json()

                jobs = data.get("jobs", [])
                if not jobs:
                    raise RuntimeError(
                        f"Slurm API returned no job for job ID {job_id}"
                    )

                states = jobs[0].get("job_state", [])
                if not states:
                    raise RuntimeError(
                        f"Slurm API returned no state for job ID {job_id}"
                    )

                state = states[0]

                logger.info("Slurm job %s is %s", job_id, state)

                if state == "COMPLETED":
                    return

                FAILED_STATES = {
                    "FAILED",
                    "CANCELLED",
                    "TIMEOUT",
                    "OUT_OF_MEMORY",
                    "NODE_FAIL",
                    "BOOT_FAIL",
                }

                if state in FAILED_STATES:
                    raise RuntimeError(
                        f"Slurm job {job_id} finished unsuccessfully: {state}"
                    )

                await asyncio.sleep(poll_interval)
        
