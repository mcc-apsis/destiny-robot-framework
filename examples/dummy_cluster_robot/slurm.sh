#!/bin/bash
#SBATCH --job-name=dummy
#SBATCH --time=00:01:00

set -e

BATCH_DIR="$1"

echo "hello" > "${BATCH_DIR}/predictions.txt"

touch "${BATCH_DIR}/finished"