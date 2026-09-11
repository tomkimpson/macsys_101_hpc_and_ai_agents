# Three scripts on Slurm

Companion repo for *From Supercomputers to AI Agents*. One piece of science,
run three ways: once, then as two different kinds of array job.

The system is an **Ornstein–Uhlenbeck process**, the canonical noisy
relaxation. A quantity is pulled back towards a mean at rate `theta` and
kicked by white noise of amplitude `sigma`:

```
dx = theta * (mu - x) dt + sigma dW
```

The transition density is exactly Gaussian, so both the simulation and the
likelihood are exact — no discretisation error to argue about, and we always
know the right answer. `ou.py` holds the model; the numbered scripts use it.

## The three scripts

| | Script | What it does | Figure |
|---|---|---|---|
| **01** | `01_mcmc.py` | Fit **one** realisation by MCMC | `posterior.png` |
| **02** | `02_inference.py` | Array: fit **a hundred** realisations | `inference.png` |
| **03** | `03_ensemble.py` | Array: **simulate** a hundred, no fitting | `ensemble.png` |

02 and 03 are the two things that can go on an array axis, and they answer
different questions.

**02 — the ensemble of inference.** One posterior cannot tell you whether
your error bars are right. A hundred can: if they are honest, the pull
`(posterior mean − truth) / posterior sd` is a unit Gaussian and the truth
sits inside the 68% interval 68% of the time. This is the check you want
after anyone — an agent included — has edited your likelihood.

**03 — the ensemble of realisations.** The spread of the process itself,
checked against the analytic envelope. It fans out from `x0` and settles
into the stationary band: the shape of an ensemble weather forecast, for the
same reason.

Each of 02 and 03 runs as an array task by default and makes its own figure
with `--collate`, so there are no separate collator files.

Honest caveat on 03: this particular forward model takes milliseconds, so on
a laptop you would just loop. It is laid out as an array because that is the
structure that survives contact with a real forward model — an operational
weather centre runs ~50 members as ~50 independent integrations precisely
because one member is hours of compute.

## Setup

Written for **OzSTAR** (Swinburne). `python-scientific` supplies numpy, scipy
and matplotlib; the venv adds `emcee` and `corner` on top of them, which is why
it is created with `--system-site-packages`.

```bash
module purge
module load python-scientific/3.11.3-foss-2023a   # OzSTAR; adjust for your site
python3 -m venv --system-site-packages /fred/oz022/$USER/venvs/macsys
source /fred/oz022/$USER/venvs/macsys/bin/activate
pip install -r requirements.txt
```

Once, from the login node. Every job script then repeats the `module load` and
the `source`, because a batch job starts in a fresh shell that has inherited
none of it.

The scripts are set to `--account=oz022` and `--partition=skylake`. Change the
account if you are on a different project; `sinfo -s` lists the partitions.

## Run it

```bash
./01_run.sh                                     # on your laptop, first
sbatch 01_run.sh                                # one job, on the cluster
jobreport <jobid>                               # what did it actually use?

A=$(sbatch --parsable 02_sweep.sh)              # 100 fits, 20 at a time
sbatch --dependency=afterok:$A 02_collate.sh    # -> inference.png

B=$(sbatch --parsable 03_sweep.sh)              # 100 simulations
sbatch --dependency=afterok:$B 03_collate.sh    # -> ensemble.png

squeue --me
```

Everything also runs without Slurm:

```bash
python 01_mcmc.py
for i in $(seq 0 99); do python 03_ensemble.py --task-id $i \
    --out results/sim_$(printf '%03d' $i).npz; done
python 03_ensemble.py --collate
```

## Files

| File | What it is |
|---|---|
| `ou.py` | The model. Imported by the numbered scripts, never run alone. |
| `01_mcmc.py` / `01_run.sh` | One job. Read this one first. |
| `02_inference.py` / `02_sweep.sh` / `02_collate.sh` | The inference ensemble. |
| `03_ensemble.py` / `03_sweep.sh` / `03_collate.sh` | The realisation ensemble. |
| `CLAUDE.md` | Cluster facts an AI agent cannot guess. |

`.sh` or `.slurm` makes no difference — `sbatch` reads the file, not the
name. `01_run.sh` is written so it works both ways: `./01_run.sh` on your
laptop, `sbatch 01_run.sh` on the cluster.

## The four verbs

```
sbatch    submit          squeue --me    what am I running?
scancel   kill            sacct -j <id>  what happened to it?
```

Plus the one everybody should use and nobody does:

```
jobreport <jobid>         how much of what I asked for did I use?
```

`jobreport` is OzSTAR's own wrapper. Elsewhere the equivalent is `seff`, which
OzSTAR does not install. Either way the portable fallback is:

```
sacct -j <jobid> --format=JobID,State,Elapsed,TotalCPU,ReqMem,MaxRSS
```
