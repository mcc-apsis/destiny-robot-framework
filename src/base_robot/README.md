# Base Robot

Shared framework for implementing DESTINY enhancement robots.

The package provides common robot functionality on one machine. It consists of the main robot implementation, two execution runners, and several utility modules.

The [**`robot.py`**](https://github.com/mcc-apsis/destiny-robot-framework/blob/main/src/base_robot/robot.py) module implements the common robot workflow, including downloading references, uploading enhancements, and interacting with the DESTINY repository. The enhancement generation itself is intentionally left abstract. New robots implement this functionality by overriding the `generate_enhancement()` method.

Two execution modes are provided through separate runner classes:

* [**`PollingRunner`**](https://github.com/mcc-apsis/destiny-robot-framework/blob/main/src/base_robot/polling_runner.py) continuously polls the DESTINY repository for new enhancement batches. Once a batch of the defined size has been processed, or no work is available, it waits for a configurable interval before polling again.

* [**`BatchRunner`**](https://github.com/mcc-apsis/destiny-robot-framework/blob/main/src/base_robot/batch_runner.py) processes all currently available enhancement batches of the defined size and terminates once no further work is available.

Several utility modules support the common functionality of all robots:

* **`config.py`** defines the robot configuration using Pydantic Settings. It loads configuration values from the environment (typically via a `.env` file) and provides a central location for robot-specific settings.

* **`client.py`** creates and configures the client used to communicate with the DESTINY repository, including authentication and HTTP settings.

* **`robot_logging.py`** configures the logging infrastructure used throughout the robot framework.

* **`version.py`** provides utilities for reading and exposing the robot version from the `pyproject.toml`.

## Configuration

The following environment variables configure the robot:

| Variable                 | Explanation                                                                    |
| ------------------------ | ------------------------------------------------------------------------------ |
| `DESTINY_REPOSITORY_URL` | URL of the DESTINY repository API the robot connects to.                       |
| `ROBOT_ID`               | Unique identifier of the robot registered with DESTINY.                        |
| `ROBOT_SECRET`           | Secret used to authenticate the robot with the DESTINY repository.             |
| `ENV`                    | Environment in which the robot runs, e.g. `local`, `staging`, or `production`. |
| `BATCH_SIZE`             | Number of references processed in a single batch.                              |
