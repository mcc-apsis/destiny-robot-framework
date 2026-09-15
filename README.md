# destiny-robot-framework

Framework for creating DESTINY robots.

This repository contains two frameworks for building robots that interact with the [DESTINY repository](https://github.com/destiny-evidence/destiny-repository):

* **`base_robot`** performs all robot actions in a single run: downloading references, processing them, and uploading the corresponding enhancements.
* **`cluster_robot`** is designed for processing references on a SLURM cluster. It first downloads the references and starts a SLURM job to process them. After the processing has finished, the robot needs to be started again to upload the resulting enhancements. Additonally, one can use a `wait` command to call a pre-defined SLURM-API and check the status of the SLURM job. 

## Create a new robot 

We use [uv](https://docs.astral.sh/uv/) to manage the Python environment and dependencies. If you don't have `uv` installed, install it with:
```
curl -LsSf https://astral.sh/uv/install.sh | sh
```
### Base Robot
To create a new base robot, probably the most common robot framework, you can use a template. Simply run:
```
uvx copier copy https://github.com/mcc-apsis/destiny-robot-framework.git my-robot

``` 
Copier will ask for the robot name:
```
Name of the robot:
```
The template generates the corresponding project structure and implementation skeleton:
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
After creating the robot, install its dependencies with:
```
cd my-robot
uv sync
```
Copy the local environment file which contains the robot-ID of a local DESTINY-repository db-dumb :
```
cp .env.local.example .env
``` 
Add your robot-specific code in `robot.py`. 

You can test your robot against a locally running DESTINY repository.
See here to get a locally running repo. Please make sure that there are enhancement batches.

Run your robot with
```
uv run python -m my-robot
```
### Cluster Robot
## Create a new robot 

We use [uv](https://docs.astral.sh/uv/) to manage the Python environment and dependencies. If you don't have `uv` installed, install it with:
```
curl -LsSf https://astral.sh/uv/install.sh | sh
```
### Base Robot
To create a new base robot, probably the most common robot framework, you can use a template. Simply run:
```
uvx copier copy https://github.com/mcc-apsis/destiny-robot-framework.git my-robot

``` 
Copier will ask for the robot name:
```
Name of the robot:
```
The template generates the corresponding project structure and implementation skeleton:
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
After creating the robot, install its dependencies with:
```
cd my-robot
uv sync
```
Copy the local environment file which contains the robot-ID of a local DESTINY-repository db-dumb :
```
cp .env.local.example .env
``` 
Add your robot-specific code to `robot.py`.

In `main.py`, you can choose between two different ways of operating the robot:

- **`PollingRunner`** continuously polls for new batches at a given time interval. Configure the `polling_interval` and `batch_size` variables.
- **`BatchRunner`** downloads all available batches and shuts down once they have been processed. Configure the `batch_size` variable.

You can test your robot against a locally running DESTINY repository.
See here to get a locally running repo. Please make sure that there are enhancement batches.

Run your robot with
```
uv run python -m my-robot
```
### Cluster Robot
A cluster robot is a robot that performs its processing on a computing cluster using SLURM.

As a starting point, we recommend using the dummy_cluster_robot in the examples directory.

A cluster robot typically consists of three stages:

Prepare – download references from the DESTINY repository, prepare the input, and submit a SLURM job.
Wait – wait for the submitted SLURM job to finish.
Process – retrieve and parse the SLURM output and upload the resulting enhancements to the DESTINY repository.

Robot-specific code, such as preparing the input for the SLURM job from the downloaded references and parsing the output into Enhancement objects, goes into robot.py. The required SLURM script also needs to be implemented.

#### 1. Prepare

Download the references and submit the SLURM job:
```
uv run python -m my-robot prepare
```
This stage downloads the references that need to be processed and submits the SLURM job.

#### 2. Wait

Wait for the submitted SLURM job to finish:
```
uv run python -m my-robot wait
```
The wait stage calls the SLURM REST API to check the status of the submitted job using its job ID.

It expects the following environment variables:

- `SLURM_USER` – the SLURM user
- `SLURM_TOKEN` – a JWT token for authentication with the SLURM REST API
- `SLURM_API` – the URL of the SLURM REST API

For example:
```
export SLURM_USER=$USER
export SLURM_TOKEN="$(scontrol token lifespan=172800)"
export SLURM_API="https://<slurm-api-url>"
```
#### 3. Process

After the SLURM job has finished, parse its output and upload the resulting enhancements:
```
uv run python -m my-robot upload
```
The `upload` stage is responsible for retrieving the SLURM output, parsing it into `Enhancement` objects, and uploading the enhancements to the DESTINY repository.

#### Workspace

For each enhancement batch, i.e. a certain number of references, a directory is created in `workspace/`. The directory is named using the batch UID.

The batch directory contains the input and output files exchanged with the SLURM job, as well as metadata about the processing.

A typical workspace looks like:

```text
workspace/
└── <batch-uid>/
    ├── input/
    │   └── references.jsonl
    ├── output/
    │   └── predictions.jsonl
    ├── metadata.json
    └── completed
```

The `references.jsonl` file contains the references downloaded during the `prepare` stage. The SLURM job writes its results to `predictions.jsonl`.

Additional metadata about the batch and SLURM job is stored in the batch directory. Once the results have been successfully uploaded and the batch has been acknowledged by the DESTINY repository, a `completed` file is created to mark the batch as processed.

## Examples

The `examples` directory contains three simple robot implementations:

### Based on `base_robot`

* **`query_robot`** simply generates boolean enhancements indicating that all references returned by a query are included.
* **`dummy_classification_robot`** demonstrates how to use a classifier within a robot.

### Based on `cluster_robot`

* **`dummy_cluster_robot`** demonstrates how to start a dummy SLURM job.

## Scripts

The `scripts` directory contains useful scripts for:

* creating enhancement batches using a free text search

## Useful Resources
More documentation can be found [here](...).
