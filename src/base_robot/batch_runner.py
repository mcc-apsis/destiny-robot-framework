import logging

import destiny_sdk

from base_robot.config import PollingRobotSettings
from base_robot.robot import BaseRobot

logger = logging.getLogger(__name__)


class BatchRunner:
    """Process all available DESTINY enhancement batches and then exit."""

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
    ) -> bool:
        """Process a single enhancement batch.

        Returns:
            True if the batch was processed successfully.
            False if processing failed.
        """

        try:
            await self.robot.process_batch(batch)

            self.client.send_robot_enhancement_batch_result(
                destiny_sdk.robots.RobotEnhancementBatchResult(
                    request_id=batch.id,
                )
            )

            logger.info(
                "Successfully processed batch %s",
                batch.id,
            )

            return True

        except Exception as exc:
            logger.exception(
                "Failed to process batch %s",
                batch.id,
            )

            self.client.send_robot_enhancement_batch_result(
                destiny_sdk.robots.RobotEnhancementBatchResult(
                    request_id=batch.id,
                    error=destiny_sdk.robots.RobotError(
                        message=f"Failed to process request: {exc}",
                    ),
                )
            )

            return False

    async def run(self) -> None:
        """Process all currently available batches and then exit."""

        logger.info(
            "Starting %s batch runner",
            self.robot.source_name,
        )
        logger.info(
            "Batch size: %d",
            self.settings.batch_size,
        )

        processed_batches = 0
        failed_batches = 0

        while True:
            batch = self.client.poll_robot_enhancement_batch(
                robot_id=self.settings.robot_id,
                limit=self.settings.batch_size,
            )

            if batch is None:
                logger.info(
                    "No enhancement batches available. "
                    "Processed %d batch(es), with %d failure(s). "
                    "Exiting.",
                    processed_batches,
                    failed_batches,
                )
                return

            logger.info(
                "Found batch %s",
                batch.id,
            )

            success = await self.handle_batch(batch)

            processed_batches += 1

            if not success:
                failed_batches += 1