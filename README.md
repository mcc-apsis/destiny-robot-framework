# destiny-robot-framework

Framework for creating DESTINY robots.

This repository contains two frameworks for building robots that interact with the DESTINY repository:

* **`base_robot`** performs all robot actions in a single run: downloading references, processing them, and uploading the corresponding enhancements.
* **`cluster_robot`** is designed for processing references on a SLURM cluster. It first downloads the references and starts a SLURM job to process them. After the processing has finished, the robot needs to be started again to upload the resulting enhancements.

## Examples

The `examples` directory contains three simple robot implementations:

### Based on `base_robot`

* **`query_robot`** simply generates boolean enhancements indicating that all references returned by a query are included.
* **`dummy_classification_robot`** demonstrates how to use a classifier within a robot.

### Based on `cluster_robot`

* **`dummy_cluster_robot`** demonstrates how to start a dummy SLURM job.

## Create a new robot 

We use [uv](https://docs.astral.sh/uv/) to manage the Python environment and dependencies. If you don't have `uv` installed, install it with:
```
curl -LsSf https://astral.sh/uv/install.sh | sh
```
To create a new robot from the template, run:
```
uv run copier copy https://github.com/mcc-apsis/destiny-robot-framework.git my-robot
``` 
Copier will ask for the robot type and name:
```
Which type of robot do you want to create? [base_robot/cluster_robot]:
Name of the robot:
```
The template generates the corresponding project structure and implementation skeleton. For example, a base_robot might contain:
``` 
my-robot/
├── .env.local.example
├── pyproject.toml
└── src/
    ├── __init__.py
    ├── config.py
    ├── main.py
    └── robot.py
```
A cluster_robot additionally contains the SLURM script required for cluster processing. After creating the robot, install its dependencies with:
```
cd my-robot
uv sync
``` 
Copy and configure the local environment file:
```
cp .env.local.example .env
``` 
## Scripts

The `scripts` directory contains useful scripts for:

* registering a robot
* creating enhancement batches

More documentation can be found [here](...).
