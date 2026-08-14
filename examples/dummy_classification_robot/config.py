import sys
from functools import lru_cache
from pathlib import Path

from pydantic import Field

sys.path.append(str(Path(__file__).resolve().parent.parent))

from base_robot.config import PollingRobotSettings


class Settings(PollingRobotSettings):
    model_path: Path = Field(
        default=Path(__file__).parent / "models" / "classifier.joblib"
    )

@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()    # type: ignore[call-arg]