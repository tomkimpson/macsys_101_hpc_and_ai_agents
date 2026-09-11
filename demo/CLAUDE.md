# CLAUDE.md

Everything here is a fact about *our* cluster and *our* project that you
cannot work out by reading the code. Get these wrong and jobs get rejected.

## Where we are

- Cluster: **OzSTAR / Ngarrgu Tindebeek**, Swinburne (`ozstar.swin.edu.au`).
  The login nodes are called `farnarkle1` / `farnarkle2`.
- Scheduler: **Slurm**. Modules are **Lmod** (`module spider` to search).
- Project account: `oz022`. Every `sbatch` needs `--account=oz022`.
- Partitions we may use: `skylake` (CPU, the default), `milan` (CPU, newer),
  `milan-gpu` / `skylake-gpu` (GPU), `datamover` (large transfers only).
  **Do not invent partition names.** If unsure, run `sinfo -s` and read.
- Project storage: `/fred/oz022/`. Not backed up. `$HOME` is 20 GB and
  backed up: code there, data and venvs in `/fred`.

## Environment

```bash
module purge
module load python-scientific/3.11.3-foss-2023a
source /fred/oz022/${USER}/venvs/macsys/bin/activate
```

Every job script must do this. There is no usable system Python.

- There is **no bare `Python/x.y.z` module on OzSTAR** — it is
  `python-scientific/<version>-foss-<year>`, which bundles numpy, scipy,
  matplotlib, pandas and astropy.
- `emcee` and `corner` are not in any module, which is the only reason the
  venv exists. It was made with `--system-site-packages` so it sits on top of
  `python-scientific` rather than rebuilding numpy. Do not recreate it without
  that flag.
- `module purge` leaves `nvidia/.latest` and `slurm/.latest` loaded and says
  so on stderr. That is normal; it is not an error to chase.

## The code

- `ou.py` — the Ornstein-Uhlenbeck model: `simulate`, `envelope`,
  `log_prob`, `fit`. Imported by the numbered scripts; it has no CLI and is
  never run on its own.
- `01_mcmc.py` — fits ONE realisation, writes `posterior.png`. ~3 s.
- `02_inference.py` — array task: fits realisation *i*, writes
  `results/fit_NNN.npz`. With `--collate`, reads them all and writes
  `inference.png` (the pull histogram). ~3 s per task.
- `03_ensemble.py` — array task: SIMULATES realisation *i*, no fitting,
  writes `results/sim_NNN.npz`. With `--collate`, writes `ensemble.png`
  (trajectories against the analytic envelope). Milliseconds per task, so
  do not give it 02's resource request.
- 02 and 03 share `results/` but use distinct prefixes (`fit_`, `sim_`).
  Keep it that way — the two collators glob for their own prefix.
- The array index *is* the noise realisation (`--task-id` seeds the RNG).
  Tasks must therefore have distinct ids, or you get duplicate realisations
  and the coverage test silently lies.
- `TRUTH`, `X0`, `DT` and `N_STEPS` in `ou.py` define the process. Every
  task must use the same values or the ensemble is not an ensemble.

## House rules for jobs

- Always throttle arrays: `--array=0-99%20`. Never submit an unthrottled
  array larger than 50 tasks — it is antisocial and our fair-share score
  pays for it.
- Right-size requests. Check with `jobreport <jobid>` after a job finishes and
  bring `--mem` and `--time` down to roughly 1.5x what was actually used.
  Over-requesting is the main reason jobs sit in the queue.
  **`seff` does not exist on OzSTAR** and neither does `jobstats` (it is
  installed but broken). Use `jobreport`, or
  `sacct -j <id> --format=JobID,State,Elapsed,TotalCPU,ReqMem,MaxRSS`.
- Logs go to `logs/`, named `%x-%j.out` (or `%x-%A_%a.out` for arrays).
- Never run the simulation on the login node. Use `sinteractive` to debug.

## Things to ask me before doing

- Submitting anything with more than 100 tasks, or `--time` over 4 hours.
- `scancel` on anything you did not submit yourself in this session.
  Never `scancel -u $USER` — it kills my other work.
- Changing `TRUTH`, `X0`, `DT` or `N_STEPS` in `ou.py`, which invalidates
  every result already on disk.
