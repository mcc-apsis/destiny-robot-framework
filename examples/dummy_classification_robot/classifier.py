import logging
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path

logger = logging.getLogger(__name__)


MODEL_PATH = (
    Path(__file__).resolve().parent
    / "models"
    / "relevance_classifier.joblib"
)

import joblib


@dataclass
class Paper:
    title: str | None
    abstract: str | None


class Classifier:
    def __init__(self, model_path: Path | None = None):
        if model_path is None:
            model_path = MODEL_PATH
        self.pipeline = joblib.load(model_path)

    @staticmethod
    def _paper_to_text(paper: Paper) -> str:
        return f"{paper.title or ''} {paper.abstract or ''}"

    def predict_proba(
        self,
        titles: Sequence[str],
        abstracts: Sequence[str],
        ) -> list[float]:

        texts = [
            f"{title} {abstract}"
            for title, abstract in zip(titles, abstracts)
        ]

        predictions = self.pipeline.predict_proba(texts)

        return [p[1] for p in predictions]