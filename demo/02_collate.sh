#!/bin/bash
# Gather the fits and make inference.png. Depends on the array:
#   sbatch --dependency=afterok:<array-job-id> 02_collate.sh
# Slurm holds this job until every task of the array has exited cleanly.

#SBATCH --job-name=fit-collate
#SBATCH --account=punimXXXX            # <-- EDIT
#SBATCH --partition=cascade            # <-- CHECK
#SBATCH --time=00:05:00
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --mem=4G
#SBATCH --output=logs/%x-%j.out

set -euo pipefail

module purge
module load foss/2022a Python/3.10.4
source "${HOME}/venvs/macsys/bin/activate"

srun python 02_inference.py --collate --results results --out inference.png
