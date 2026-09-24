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

## Implementation

To create a new base robot, the most common robot framework, you can use the provided template. Simply run:

```bash
uvx copier copy https://github.com/mcc-apsis/destiny-robot-framework.git my-robot
```

Copier will ask for the robot name:

```text
Name of the robot:
```

The template generates the corresponding project structure and implementation skeleton:

```text
my-robot/
├── .env.local.example
├── pyproject.toml
└── src/
    ├── __init__.py
    ├── config.py
    ├── main.py
    └── robot.py
```
* **robot.py** implements the enhancement logic by subclassing `BaseRobot` and providing an implementation of `generate_enhancement()`. The **only function** that must be implemented for a minimal custom robot is `generate_enhancement()`.
* **main.py** initializes the robot, loads the configuration, creates the required clients, and serves as the application's entry point.
* **config.py** defines the robot-specific configuration. It can include additional settings such as model locations, classifier parameters, or custom runtime options.
* **pyproject.toml** defines the project metadata and robot version, which is reported to the DESTINY repository during execution.

After creating the robot, install its dependencies with:

```bash
cd my-robot
uv sync
```

Copy the local environment file:

```bash
cp .env.local.example .env
```

Add your robot-specific code in `robot.py`.

You can test your robot against a locally running DESTINY repository. See the [local DESTINY repository instructions](https://github.com/mcc-apsis/destiny-robot-framework/wiki/7-Run-a-local-Destiny-Repo) and make sure that enhancement batches are available.

Run your robot with:

```bash
uv run python -m my-robot
```



## Try out the examples

Minimal example implementations are provided in the repository. The [`query_robot`](https://github.com/mcc-apsis/destiny-robot-framework/tree/main/examples/query_robot) demonstrates the smallest possible robot implementation, while the [`dummy_classification_robot`](https://github.com/mcc-apsis/destiny-robot-framework/tree/main/examples/dummy_classification_robot) demonstrates how a machine learning model can be integrated into the framework.

Assuming that a [local DESTINY repository](https://github.com/mcc-apsis/destiny-robot-framework/wiki/7-Run-a-local-Destiny-Repo) is running, the robot folder contains a [`.env` file ](https://github.com/mcc-apsis/destiny-robot-framework/wiki/7-Run-a-local-Destiny-Repo#create-and-receive-batches), provided by the template in env.local and [enhancement batches ](https://github.com/mcc-apsis/destiny-robot-framework/wiki/7-Run-a-local-Destiny-Repo#create-and-receive-batches) are available, the query robot can be started from the `query_robot` folder with

```javascript
uv run python -m query_robot
```

The `dummy_classifier_robot` needs a model to be trained, instructions can be found in [`models`](https://github.com/mcc-apsis/destiny-robot-framework/blob/main/examples/dummy_classification_robot/models/train_test_model.py). Once this is done the robot is started from the `dummy_classification folder` with

```javascript
uv run python -m dummy_classification_robot
```

## Configuration

The following environment variables configure the robot:

| Variable                 | Explanation                                                                    |
| ------------------------ | ------------------------------------------------------------------------------ |
| `DESTINY_REPOSITORY_URL` | URL of the DESTINY repository API the robot connects to.                       |
| `ROBOT_ID`               | Unique identifier of the robot registered with DESTINY.                        |
| `ROBOT_SECRET`           | Secret used to authenticate the robot with the DESTINY repository.             |
| `ENV`                    | Environment in which the robot runs, e.g. `local`, `staging`, or `production`. |
| `BATCH_SIZE`             | Number of references processed in a single batch.                              |
