"""Wrapper around Slurm job submission."""

import logging
import shutil
import subprocess
from pathlib import Path

from cluster_robot.batch import BatchStore

logger = logging.getLogger(__name__)

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
            return "local"

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
        
