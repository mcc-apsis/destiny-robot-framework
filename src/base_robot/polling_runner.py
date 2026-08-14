import asyncio
import contextlib
import logging
import signal
from types import FrameType

import destiny_sdk

from base_robot.config import PollingRobotSettings
from base_robot.robot import BaseRobot

logger = logging.getLogger(__name__)

class PollingRunner:
    """Continuously poll the DESTINY repository for enhancement batches."""

    def __init__(
        self,
        robot: BaseRobot,
        client: destiny_sdk.client.Client,
        settings: PollingRobotSettings,
    ) -> None:
        self.robot = robot
        self.client = client
        self.settings = settings

    async def handle_batch(
        self,
        batch: destiny_sdk.robots.RobotEnhancementBatch,
    ) -> None:
        """Process a single enhancement batch."""

        try:
            await self.robot.process_batch(batch)

            self.client.send_robot_enhancement_batch_result(
                destiny_sdk.robots.RobotEnhancementBatchResult(
                    request_id=batch.id,
                )
            )

            logger.info("Successfully processed batch %s", batch.id)

        except Exception as exc:
            logger.exception("Failed to process batch %s", batch.id)

            self.client.send_robot_enhancement_batch_result(
                destiny_sdk.robots.RobotEnhancementBatchResult(
                    request_id=batch.id,
                    error=destiny_sdk.robots.RobotError(
                        message=f"Failed to process request: {exc}"
                    ),
                )
            )

    async def poll_forever(self) -> None:
        """Continuously poll for enhancement batches."""

        while True:
            try:
                batch = self.client.poll_robot_enhancement_batch(
                    robot_id=self.settings.robot_id,
                    limit=self.settings.batch_size,
                )

                if batch is None:
                    await asyncio.sleep(self.settings.poll_interval_seconds)
                    continue

                logger.info("Found batch %s", batch.id)

                await self.handle_batch(batch)

            except Exception:
                logger.exception("Unexpected error during polling")

            await asyncio.sleep(self.settings.poll_interval_seconds)    

    async def run(self) -> None:
        """Continuously poll for batches."""

        logger.info(
            "Starting %s polling loop",
            self.robot.source_name,
        )
        logger.info(
            "Polling interval: %d seconds",
            self.settings.poll_interval_seconds,
        )
        logger.info(
            "Batch size: %d",
            self.settings.batch_size,
        )

        shutdown_event = asyncio.Event()

        def signal_handler(signum: int, _frame: FrameType | None) -> None:
            logger.info(
                "Received signal %s, initiating graceful shutdown...",
                signum,
            )
            shutdown_event.set()

        # Register signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)

        poll_task = asyncio.create_task(self.poll_forever())

        try:
            _, pending = await asyncio.wait(
                [
                    poll_task,
                    asyncio.create_task(shutdown_event.wait()),
                ],
                return_when=asyncio.FIRST_COMPLETED,
            )

            for task in pending:
                task.cancel()
                with contextlib.suppress(asyncio.CancelledError):
                    await task

            logger.info("Shutdown complete")

        except Exception:
            logger.exception("Fatal error occurred")
            raise