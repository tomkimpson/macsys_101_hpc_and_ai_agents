#!/bin/bash
# 03 -- the ensemble of REALISATIONS. A hundred forward simulations, no
# fitting. Same array structure as 02, a fraction of the cost.
#
#   sbatch 03_sweep.sh
#
# Note the resource request: these tasks take milliseconds, so asking for
# 5 minutes and 2G each would be dishonest and would queue you behind
# people who asked properly. Right-size every array separately.

#SBATCH --job-name=sim-many
#SBATCH --account=oz022                # your OzSTAR project  <-- EDIT
#SBATCH --partition=skylake            # default CPU pool     <-- CHECK
#SBATCH --time=00:01:00                # per TASK
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --mem=500M                     # per TASK
#SBATCH --array=0-99%20
#SBATCH --output=logs/%x-%A_%a.out

set -euo pipefail

module purge
module load python-scientific/3.11.3-foss-2023a
source "/fred/oz022/${USER}/venvs/macsys/bin/activate"

echo "task ${SLURM_ARRAY_TASK_ID} of array ${SLURM_ARRAY_JOB_ID} on $(hostname)"

mkdir -p results

srun python 03_ensemble.py \
    --task-id "${SLURM_ARRAY_TASK_ID}" \
    --out "results/sim_$(printf '%03d' "${SLURM_ARRAY_TASK_ID}").npz"
