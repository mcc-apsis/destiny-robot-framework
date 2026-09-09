"""Create enhancement requests against a DESTINY repository.

Reference search is performed using the DESTINY OAuth client.
Enhancement requests are created using HMAC robot authentication.

Configuration is read from a JSON file containing:

    repository_url
    env_file
    query
    number_of_references

The robot ID and secret are read from the configured .env.destiny file.

Run with:

    uv run create_enhancement_requests.py config.json
"""

import json
import sys
from pathlib import Path
from uuid import UUID

import httpx
from destiny_sdk.client import HMACSigningAuth, OAuthClient


def load_config(config_path: str) -> dict:
    """Load configuration from a JSON file."""

    path = Path(config_path)

    with path.open() as file:
        return json.load(file)


def load_env_file(env_path: str) -> dict[str, str]:
    """Load key-value pairs from an environment file."""

    path = Path(env_path)

    with path.open() as env_file:
        env = {}

        for line in env_file:
            line = line.strip()

            if not line or line.startswith("#"):
                continue

            key, value = line.split("=", 1)
            env[key.strip()] = value.strip().strip('"').strip("'")

    return env


def get_reference_ids(
    client: httpx.Client,
    query: str,
    number_of_references: int | None = None,
    use_api_v1_prefix: bool = True,
) -> list[str]:
    """Retrieve reference IDs using the configured client."""

    reference_ids: list[str] = []
    page = 1

    search_path = (
        "/v1/references/search/"
        if use_api_v1_prefix
        else "/references/search/"
    )

    while (
        number_of_references is None
        or len(reference_ids) < number_of_references
    ):
        response = client.get(
            search_path,
            params={
                "q": query,
                "page": page,
            },
        )

        response.raise_for_status()

        data = response.json()
        references = data["references"]

        print(f"Page {page}: {len(references)} references")

        if not references:
            break

        reference_ids.extend(
            reference["id"]
            for reference in references
        )

        page += 1

    if number_of_references is not None:
        return reference_ids[:number_of_references]

    return reference_ids


def create_enhancement_request(
    client: httpx.Client,
    repository_url: str,
    robot_id: str,
    reference_ids: list[str],
) -> dict:
    """Create an enhancement request using HMAC authentication."""

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
    """Retrieve references with OAuth and create an enhancement request."""

    if len(sys.argv) != 2:
        print(
            "Usage: uv run create_enhancement_requests.py "
            "<config.json>"
        )
        sys.exit(1)

    config = load_config(sys.argv[1])

    repository_url = config["repository_url"].rstrip("/")
    env = load_env_file(config["env_file"])

    robot_id = env.get("ROBOT_ID")
    robot_secret = env.get("ROBOT_SECRET")

    if not robot_id:
        raise ValueError("ROBOT_ID is missing from .env.destiny")

    if not robot_secret:
        raise ValueError("ROBOT_SECRET is missing from .env.destiny")

    query = config["query"]
    number_of_references = config.get("number_of_references")

    print(f"Repository: {repository_url}")
    print(f"Robot ID: {robot_id}")
    print(f"Query: {query}")

    if number_of_references is None:
        print("Number of references: all")
    else:
        print(f"Number of references: {number_of_references}")

    # ------------------------------------------------------------------
    # 1. Search references using OAuth
    # ------------------------------------------------------------------

    print("\nSearching references using OAuth...")

    is_local = repository_url.startswith(
        (
            "http://127.0.0.1:",
            "http://localhost:",
        )
    )

    if is_local:
        print("\nUsing local repository without OAuth.")

        with httpx.Client(
            base_url=repository_url,
            timeout=30.0,
        ) as client:
            reference_ids = get_reference_ids(
                client=client,
                query=query,
                number_of_references=number_of_references,
                use_api_v1_prefix=True,
            )

    else:
        print("\nUsing staging repository with OAuth.")

        oauth_client = OAuthClient(env="staging")

        reference_ids = get_reference_ids(
            client=oauth_client.get_client(),
            query=query,
            number_of_references=number_of_references,
            use_api_v1_prefix=False,
        )

    print(f"\nUsing {len(reference_ids)} reference IDs.")

    print("\nFirst five IDs:")

    for reference_id in reference_ids[:5]:
        print(f"  {reference_id}")

    if not reference_ids:
        print("\nNo references found. Nothing to do.")
        return

    # ------------------------------------------------------------------
    # 2. Create enhancement request using HMAC robot authentication
    # ------------------------------------------------------------------

    print("\nCreating enhancement request using HMAC...")

    hmac_auth = HMACSigningAuth(
        secret_key=robot_secret,
        client_id=UUID(robot_id),
    )

    with httpx.Client(
        auth=hmac_auth,
        timeout=30.0,
    ) as client:
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