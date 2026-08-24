#!/bin/bash
#SBATCH --job-name=robot
#SBATCH --time=00:01:00

set -e

# The batch directory is passed as the first argument.
BATCH_DIR="$1"

# TODO: Process the input and write predictions to the batch directory.
echo "hello" > "${BATCH_DIR}/predictions.txt"

# The batch directory is passed as the first argument.
touch "${BATCH_DIR}/finished"