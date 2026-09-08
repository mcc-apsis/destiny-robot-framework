"""Create enhancement requests against a DESTINY repository.

Configuration is read from a JSON file containing the repository URL,
robot ID, search query, number of references, and authentication token.

Run with:

    uv run create_enhancement_requests.py config.json
"""

import json
import sys
from pathlib import Path

import httpx


def load_config(config_path: str) -> dict:
    """Load configuration from a JSON file."""

    path = Path(config_path)

    with path.open() as file:
        return json.load(file)


def get_reference_ids(
    client: httpx.Client,
    repository_url: str,
    query: str,
    number_of_references: int,
) -> list[str]:
    """Retrieve reference IDs using the standard search endpoint."""

    reference_ids: list[str] = []
    page = 1

    while len(reference_ids) < number_of_references:
        response = client.get(
            f"{repository_url}/v1/references/search/",
            params={
                "q": query,
                "page": page,
            },
        )

        response.raise_for_status()

        data = response.json()
        references = data["references"]

        print(
            f"Page {page}: "
            f"{len(references)} references"
        )

        if not references:
            break

        reference_ids.extend(
            reference["id"]
            for reference in references
        )

        page += 1

    return reference_ids[:number_of_references]


def create_enhancement_request(
    client: httpx.Client,
    repository_url: str,
    robot_id: str,
    reference_ids: list[str],
) -> dict:
    """Create an enhancement request for the references."""

    payload = {
        "robot_id": robot_id,
        "reference_ids": reference_ids,
        "source": "script",
    }

    response = client.post(
        f"{repository_url}/v1/enhancement-requests/",
        json=payload,
    )

    response.raise_for_status()

    return response.json()


def main() -> None:
    """Retrieve references and create an enhancement request."""

    if len(sys.argv) != 2:
        print(
            "Usage: uv run create_enhancement_requests.py "
            "<config.json>"
        )
        sys.exit(1)

    config = load_config(sys.argv[1])

    repository_url = config["repository_url"].rstrip("/")
    robot_id = config["robot_id"]
    query = config["query"]
    number_of_references = config["number_of_references"]
    token = config["token"]

    headers = {
        "Authorization": f"Bearer {token}",
    }

    with httpx.Client(
        headers=headers,
        timeout=30.0,
    ) as client:

        print(f"Repository: {repository_url}")
        print(f"Robot ID: {robot_id}")
        print(f"Query: {query}")
        print(
            f"Number of references: "
            f"{number_of_references}"
        )

        reference_ids = get_reference_ids(
            client=client,
            repository_url=repository_url,
            query=query,
            number_of_references=number_of_references,
        )

        print(
            f"\nUsing {len(reference_ids)} reference IDs."
        )

        print("\nFirst five IDs:")

        for reference_id in reference_ids[:5]:
            print(f"  {reference_id}")

        if not reference_ids:
            print("\nNo references found. Nothing to do.")
            return

        enhancement_request = create_enhancement_request(
            client=client,
            repository_url=repository_url,
            robot_id=robot_id,
            reference_ids=reference_ids,
        )

        print("\nEnhancement request created:")

        print(
            json.dumps(
                enhancement_request,
                indent=2,
            )
        )


if __name__ == "__main__":
    main()