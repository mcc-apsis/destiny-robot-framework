from logging import getLogger

logger = getLogger(__name__)

from destiny_sdk.enhancements import (
    AbstractContentEnhancement,
    AnnotationEnhancement,
    BibliographicMetadataEnhancement,
    BooleanAnnotation,
    Enhancement,
)
from destiny_sdk.references import Reference
from destiny_sdk.visibility import Visibility

from base_robot.robot import BaseRobot
from dummy_classification_robot.classifier import Classifier

SCHEME = "domain:inclusion"
LABEL = "cdr"

def extract_title_abstract(reference: Reference) -> tuple[str, str]:
    title = ""
    abstract = ""

    if reference.enhancements is None:
        return title, abstract

    for enhancement in reference.enhancements:
        content = enhancement.content

        if isinstance(content, BibliographicMetadataEnhancement):
            title = content.title or ""

        elif isinstance(content, AbstractContentEnhancement):
            abstract = content.abstract or ""

    return title, abstract


class ClassificationRobot(BaseRobot):
    """Robot that classifies references as relevant or not."""

    source_name = "Classification Robot"

    def __init__(
            self, 
            settings,
            robot_version: str,
            ):
        super().__init__(robot_version)

        self.classifier = Classifier(
            settings.model_path,
        )

    def generate_enhancements(self, 
                              references: list[Reference]
                              ) -> list[Enhancement]:
        
        # handle empty batches
        if not references:
            return []

        logger.info("generate_enhancements called with %d references", len(references))

        titles, abstracts = zip(
                *(extract_title_abstract(r) for r in references)
            )

        probabilities = self.classifier.predict_proba(
            titles,
            abstracts,
        )

        enhancements = []

        for reference, probability in zip(references, probabilities):

            enhancement = Enhancement(
            reference_id=reference.id,
            source=self.source_name,
            visibility=Visibility.PUBLIC,
            robot_version=self.robot_version,
            content=AnnotationEnhancement(
                annotations=[
                    BooleanAnnotation(
                        scheme=SCHEME,
                        label=LABEL,
                        value=probability >= 0.5,
                        score=probability,
                        )
                    ]
                ),
            )

        
            enhancements.append(enhancement)

        return enhancements