#!/bin/bash
# 02 -- the ensemble of INFERENCE. The same fit, a hundred times, on a
# hundred different realisations. The ONLY thing that differs between tasks
# is $SLURM_ARRAY_TASK_ID.
#
#   sbatch 02_sweep.sh

#SBATCH --job-name=fit-many
#SBATCH --account=punimXXXX            # <-- EDIT
#SBATCH --partition=cascade            # <-- CHECK
#SBATCH --time=00:05:00                # per TASK, not for the whole array
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --mem=2G                       # per TASK
#SBATCH --array=0-99%20                # 100 tasks, at most 20 at a time
#SBATCH --output=logs/%x-%A_%a.out     # %A = array id, %a = task index

set -euo pipefail

module purge
module load foss/2022a Python/3.10.4
source "${HOME}/venvs/macsys/bin/activate"

echo "task ${SLURM_ARRAY_TASK_ID} of array ${SLURM_ARRAY_JOB_ID} on $(hostname)"

mkdir -p results

srun python 02_inference.py \
    --task-id "${SLURM_ARRAY_TASK_ID}" \
    --out "results/fit_$(printf '%03d' "${SLURM_ARRAY_TASK_ID}").npz"
