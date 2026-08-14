import destiny_sdk

from base_robot.robot import BaseRobot

SCHEME = "query:inclusion"
LABEL = "cdr"


class QueryRobot(BaseRobot):
    """Robot that marks references as included."""

    source_name = "Query Robot"

    def _create_inclusion_enhancement(
    self,
    reference: destiny_sdk.references.Reference,
    ) -> destiny_sdk.enhancements.Enhancement:
        """Create an inclusion enhancement for a reference."""
        return destiny_sdk.enhancements.Enhancement(
            reference_id=reference.id,
            source=self.source_name,
            visibility=destiny_sdk.visibility.Visibility.PUBLIC,
            robot_version=self.robot_version,
            content=destiny_sdk.enhancements.AnnotationEnhancement(
                annotations=[
                    destiny_sdk.enhancements.BooleanAnnotation(
                        scheme=SCHEME,
                        label=LABEL,
                        value=True,
                        score=1.0,
                    )
                ]
            ),
        )


    def generate_enhancements(
        self,
        references: list[destiny_sdk.references.Reference],
    ) -> list[destiny_sdk.enhancements.Enhancement]:
        """Generate an 'included' enhancement for every reference."""

        enhancements = []

        for reference in references:
            enhancement = self._create_inclusion_enhancement(reference)
            enhancements.append(enhancement)

        return enhancements