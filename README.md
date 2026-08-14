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

## Scripts

The `scripts` directory contains useful scripts for:

* registering a robot
* creating enhancement batches

More documentation can be found [here](...).
