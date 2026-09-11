#!/bin/bash
# Gather the realisations and make ensemble.png. Depends on the array:
#   sbatch --dependency=afterok:<array-job-id> 03_collate.sh

#SBATCH --job-name=sim-collate
#SBATCH --account=oz022                # your OzSTAR project  <-- EDIT
#SBATCH --partition=skylake            # default CPU pool     <-- CHECK
#SBATCH --time=00:05:00
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --mem=4G
#SBATCH --output=logs/%x-%j.out

set -euo pipefail

module purge
module load python-scientific/3.11.3-foss-2023a
source "/fred/oz022/${USER}/venvs/macsys/bin/activate"

srun python 03_ensemble.py --collate --results results --out ensemble.png
