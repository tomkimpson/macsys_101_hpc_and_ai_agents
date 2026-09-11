#!/bin/bash
# 01 -- one job, one realisation. The smallest complete thing you can submit.
#
#   sbatch 01_run.sh       on the cluster
#   ./01_run.sh            on your laptop (the #SBATCH lines are just comments)
#
# The extension is irrelevant. sbatch reads the file, not the name: .sh,
# .slurm, .sbatch, no extension at all -- all identical. What matters is the
# shebang on line 1 and that every #SBATCH line comes BEFORE the first real
# command. Slurm stops reading directives at the first non-comment line.

#SBATCH --job-name=ou-fit              # what it's called in squeue
#SBATCH --account=oz022                # which project gets billed  <-- EDIT
#SBATCH --partition=skylake            # OzSTAR default CPU pool    <-- CHECK
#SBATCH --time=00:05:00                # walltime limit: HH:MM:SS
#SBATCH --ntasks=1                     # one process...
#SBATCH --cpus-per-task=1              # ...on one core
#SBATCH --mem=2G                       # memory for the whole job
#SBATCH --output=logs/%x-%j.out        # %x = job name, %j = job id
# #SBATCH --mail-type=END,FAIL         # uncomment to be emailed when it
# #SBATCH --mail-user=you@example.edu  # finishes or fails

set -euo pipefail                      # fail loudly, not silently

mkdir -p logs results

# Only load modules when we are actually on the cluster.
if [[ -n "${SLURM_JOB_ID:-}" ]]; then
    module purge
    module load python-scientific/3.11.3-foss-2023a
    source "/fred/oz022/${USER}/venvs/macsys/bin/activate"
    echo "job ${SLURM_JOB_ID} on $(hostname) starting at $(date)"
fi

python 01_mcmc.py --out posterior.png

echo "finished at $(date)"
# Then:  jobreport $SLURM_JOB_ID   -- and bring --mem and --time down to fit.
