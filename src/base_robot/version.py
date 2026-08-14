from pathlib import Path

import tomllib


def read_version(package_dir: Path) -> str:
    """Read the version from a package's pyproject.toml."""

    pyproject = package_dir / "pyproject.toml"

    with pyproject.open("rb") as toml_file:
        toml = tomllib.load(toml_file)

    try:
        return toml["project"]["version"]
    except KeyError as exc:
        raise ValueError(
            f"No project.version found in {pyproject}"
        ) from exc