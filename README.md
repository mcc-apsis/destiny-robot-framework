# Framework for creating DESTINY robots

[Wiki for this project](https://github.com/mcc-apsis/destiny-robot-framework/wiki)

[DESTINY repository documentation](https://destiny-evidence.github.io/destiny-repository/)

This repository contains two frameworks for building robots that interact with the [DESTINY repository](https://github.com/destiny-evidence/destiny-repository):

* **`base_robot`** performs all robot actions in a single run: downloading references, processing them, and uploading the corresponding enhancements.

* **`cluster_robot`** is designed for computationally intensive processing on a SLURM cluster. It separates the workflow into three stages: downloading references and submitting a SLURM job, waiting for the job to finish, and uploading the resulting enhancements.

For detailed documentation on each framework, see:

* **[`base_robot`](./src/base_robot/README.md)** — framework architecture, implementation, configuration, and examples.
* **[`cluster_robot`](./src/cluster_robot/README.md)** — cluster workflow, implementation, configuration, and examples.


## Which framework should I use?

| | `base_robot` | `cluster_robot` |
|---|---|---|
| Processing | On the robot machine | On a SLURM cluster |
| Workflow | Single run | Prepare → Wait → Upload |
| Best suited for | Lightweight processing | Computationally intensive processing |

For detailed documentation, see:
# Framework for creating DESTINY robots

[Wiki for this project](https://github.com/mcc-apsis/destiny-robot-framework/wiki)

[DESTINY repository documentation](https://destiny-evidence.github.io/destiny-repository/)

This repository provides two frameworks for building robots that interact with the [DESTINY repository](https://github.com/destiny-evidence/destiny-repository):

- **`base_robot`** — for robots that download, process, and upload references in a single run.
- **`cluster_robot`** — for computationally intensive robots that perform processing on a SLURM cluster and separate preparation, waiting, and upload into distinct stages.

## Which framework should I use?

| | `base_robot` | `cluster_robot` |
|---|---|---|
| Processing | On the robot machine | On a SLURM cluster |
| Workflow | Single run | Prepare → Wait → Upload |
| Best suited for | Lightweight processing | Computationally intensive processing |

For detailed documentation, see:

- **[`base_robot`](./src/base_robot/README.md)** — framework architecture, implementation, configuration, and examples.
- **[`cluster_robot`](./src/cluster_robot/README.md)** — cluster workflow, implementation, configuration, workspace, and examples.

## Getting started

We use [uv](https://docs.astral.sh/uv/) to manage Python environments and dependencies.

### 1. Choose a framework

Choose `base_robot` for processing that can be performed on the robot machine. Choose `cluster_robot` if the enhancement generation should run on a SLURM cluster.

### 2. Create your robot

For a new robot based on `base_robot`, use the provided Copier template:

```bash
uvx copier copy https://github.com/mcc-apsis/destiny-robot-framework.git my-robot
```

For a `cluster_robot`, start from the [`dummy_cluster_robot`](./examples/dummy_cluster_robot) example.

See the corresponding framework README for detailed implementation instructions.

### 3. Test your robot

Test the robot against a [local DESTINY repository](https://github.com/mcc-apsis/destiny-robot-framework/wiki/7-Run-a-local-Destiny-Repo) before deploying it.

The [robot testing guide](https://github.com/mcc-apsis/destiny-robot-framework/wiki/3-Robot---Testing) contains further information.

### 4. Register the robot

Once the robot has been tested successfully, [register it with the DESTINY repository](https://github.com/mcc-apsis/destiny-robot-framework/wiki/4-Robot---Registration#registering-a-robot).

### 5. Assign work

Finally, [assign work to the robot](https://github.com/mcc-apsis/destiny-robot-framework/wiki/4-Robot---Registration#assigning-work-to-a-robot).

## Examples

The `examples` directory contains minimal implementations demonstrating different types of robots.

### Based on `base_robot`

- **`query_robot`** — generates boolean enhancements indicating that all references returned by a query are included.
- **`dummy_classification_robot`** — demonstrates how to integrate a classifier into a robot.

### Based on `cluster_robot`

- **`dummy_cluster_robot`** — demonstrates how to run enhancement generation as a SLURM job.

## Scripts

The `scripts` directory contains utility scripts for working with the DESTINY repository, including creating enhancement batches from free-text searches.
- **[`base_robot`](./src/base_robot/README.md)**  
  Framework architecture, implementation, configuration, and examples.

- **[`cluster_robot`](./src/cluster_robot/README.md)**  
  Cluster workflow, implementation, configuration, workspace, and examples.

## Getting started

We use [uv](https://docs.astral.sh/uv/) to manage Python environments
and dependencies.

### 1. Choose a framework

Choose `base_robot` for processing that can be performed on the robot
machine. Choose `cluster_robot` if the enhancement generation should run
on a SLURM cluster.

### 2. Create your robot

For a new robot based on `base_robot`, use the provided Copier template:

```bash
uvx copier copy https://github.com/mcc-apsis/destiny-robot-framework.git my-robot
```



## Create a new robot

We use [uv](https://docs.astral.sh/uv/) to manage the Python environment and dependencies. If you don't have `uv` installed, install it with:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Base Robot

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

For more details, see the [`base_robot` documentation](./src/base_robot/README.md).

### Cluster Robot

A cluster robot performs its processing on a computing cluster using SLURM.

As a starting point, we recommend using the [`dummy_cluster_robot`](./examples/dummy_cluster_robot) in the `examples` directory.

A cluster robot typically consists of three stages:

1. **Prepare** – download references from the DESTINY repository, prepare the input, and submit a SLURM job.
2. **Wait** – wait for the submitted SLURM job to finish.
3. **Upload** – retrieve and parse the SLURM output and upload the resulting enhancements to the DESTINY repository.

Robot-specific code, such as preparing the input for the SLURM job and parsing its output into `Enhancement` objects, goes into `robot.py`. The required SLURM script also needs to be implemented.

#### 1. Prepare

Download the references and submit the SLURM job:

```bash
uv run python -m my-robot prepare
```

#### 2. Wait

Wait for the submitted SLURM job to finish:

```bash
uv run python -m my-robot wait
```

The `wait` stage calls the SLURM REST API to check the status of the submitted job using its job ID.

#### 3. Upload

After the SLURM job has finished, parse its output and upload the resulting enhancements:

```bash
uv run python -m my-robot upload
```

For details on the cluster workflow, configuration, workspace structure, and implementation, see the [`cluster_robot` documentation](./src/cluster_robot/README.md).

## Examples

The `examples` directory contains three simple robot implementations.

### Based on `base_robot`

* **`query_robot`** simply generates boolean enhancements indicating that all references returned by a query are included.
* **`dummy_classification_robot`** demonstrates how to use a classifier within a robot.

### Based on `cluster_robot`

* **`dummy_cluster_robot`** demonstrates how to run a robot using a SLURM job.

## Scripts

The `scripts` directory contains useful scripts for:

* creating enhancement batches using a free-text search

## I created my robots - now what?
Once you implemented your robot, and [tested it locally](https://github.com/mcc-apsis/destiny-robot-framework/wiki/3-Robot---Testing) to let it run properly, you need to [register](https://github.com/mcc-apsis/destiny-robot-framework/wiki/4-Robot---Registration#registering-a-robot) it at the DEstiny repository and [assign work](https://github.com/mcc-apsis/destiny-robot-framework/wiki/4-Robot---Registration#assigning-work-to-a-robot) to it.
