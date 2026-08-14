from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parent.parent))

from relevance_robot.classifier import RelevanceClassifier


def main():
    classifier = RelevanceClassifier()

    titles = [
        "Biochar improves soil carbon sequestration",
        "Economic impacts of renewable energy subsidies",
        "Direct Air Capture with solid sorbents",
    ]

    abstracts = [
        (
            "We investigate the effectiveness of biochar as a carbon "
            "dioxide removal technology using field experiments."
        ),
        (
            "This paper analyses government subsidy schemes for wind and "
            "solar energy in Europe."
        ),
        (
            "A techno-economic assessment of direct air capture systems "
            "using solid sorbents."
        ),
    ]

    probabilities = classifier.predict_proba(titles, abstracts)

    print(f"Loaded model\n")

    for title, probability in zip(titles, probabilities):
        print(f"Title       : {title}")
        print(f"Probability : {probability:.3f}")
        print(f"Relevant    : {probability >= 0.5}")
        print("-" * 60)


if __name__ == "__main__":
    main()