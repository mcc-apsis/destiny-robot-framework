"""Create an enhancement request against a locally running DESTINY repository.

The script retrieves a specified number of reference IDs from the local
repository using the standard reference search endpoint and creates an
enhancement request for those references using a robot registered in the
local repository database.

This script is intended for local testing only. The DESTINY repository must
already be running at ``REPOSITORY_URL``, and ``ROBOT_ID`` is a UUID of
a robot registered in the local database.

Run with uv:

    uv run create_enhancement_requests.py
"""

import json

import httpx

REPOSITORY_URL = "http://127.0.0.1:8000"

# Replace with the UUID of the robot that should process the references.
ROBOT_ID = "cb73f9a3-af2a-4bfa-9502-f61d5fe18b11"

# Number of reference IDs to include in the enhancement request.
NUMBER_OF_REFERENCES = 100


def get_reference_ids(
    number_of_references: int,
) -> list[str]:
    """Retrieve reference IDs using the standard search endpoint."""

    reference_ids: list[str] = []

    page = 1

    while len(reference_ids) < number_of_references:

        response = httpx.get(
            f"{REPOSITORY_URL}/v1/references/search/",
            params={
                "q": "*:*",
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

        # No more results are available.
        if not references:
            break

        page_reference_ids = [
            reference["id"]
            for reference in references
        ]

        reference_ids.extend(
            page_reference_ids
        )

        page += 1

    return reference_ids[:number_of_references]


def create_enhancement_request(
    reference_ids: list[str],
) -> dict:
    payload = {
        "robot_id": ROBOT_ID,
        "reference_ids": reference_ids,
        "source": "local-test",
    }

    response = httpx.post(
        f"{REPOSITORY_URL}/v1/enhancement-requests/",
        json=payload,
        timeout=30.0,
    )

    return response.json()


def main() -> None:
    """Retrieve reference IDs and request enhancements."""

    reference_ids = get_reference_ids(
        number_of_references=NUMBER_OF_REFERENCES,
    )

    print(
        f"\nUsing {len(reference_ids)} reference IDs."
    )

    print("\nFirst five IDs:")

    for reference_id in reference_ids[:5]:
        print(f"  {reference_id}")

    enhancement_request = create_enhancement_request(
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