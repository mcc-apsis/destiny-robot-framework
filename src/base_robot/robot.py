"""Enhancement processing logic for a generic robot."""

import logging
from abc import ABC, abstractmethod

import destiny_sdk
import httpx

logger = logging.getLogger(__name__)

class BaseRobot(ABC):
    """Handles the processing of robot enhancement batches."""
    source_name: str
    upload_headers: dict[str, str] = {
                    "Content-Type": "application/jsonl",
                    "x-ms-blob-type": "BlockBlob"
                }

    def __init__(self, robot_version: str) -> None:
        """Initialize the processor with configuration."""
        self.robot_version = robot_version


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
    def generate_enhancements(
        self,
        references: list[destiny_sdk.references.Reference],
    ) -> list[destiny_sdk.enhancements.Enhancement]:
        """Generate enhancements for a batch of references."""
        pass

    
    async def upload_enhancements(
        self,
        enhancements: list[destiny_sdk.enhancements.Enhancement],
        result_storage_url: str,
    ) -> None:
        """Upload enhancements to storage URL."""
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

    async def process_batch(
        self, batch: destiny_sdk.robots.RobotEnhancementBatch
    ) -> list[destiny_sdk.enhancements.Enhancement]:
        """Process a batch by downloading references and creating enhancements."""
        logger.info("Processing robot enhancement batch %s", batch.id)
        
        references = await self.download_references(
            str(batch.reference_storage_url)
        )

        enhancements = self.generate_enhancements(references)

        await self.upload_enhancements(
            enhancements,
            str(batch.result_storage_url),
        )

        return enhancements