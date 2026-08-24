from functools import lru_cache
from pathlib import Path

from pydantic_settings import SettingsConfigDict

from base_robot.config import PollingRobotSettings


class Settings(PollingRobotSettings):
    model_config = SettingsConfigDict(
        env_file=Path(__file__).parent / ".env",
        env_file_encoding="utf-8",
    )


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()  # type: ignore[call-arg]