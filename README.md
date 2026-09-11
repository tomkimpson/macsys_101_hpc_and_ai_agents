# From Supercomputers to AI Agents

Slides and demo code for a MACSYS 101 talk on modern workflows for
high-performance computing. Two halves:

- **Part 1 — Slurm.** How to run intensive computations on a remote machine.
- **Part 2 — AI agents.** How to get an agent to write and debug your code.

## What to look at

**[`slides.pdf`](slides.pdf)** — the talk. Written in Marp; the source is
[`slides.md`](slides.md) and `make pdf` rebuilds it.

**[`demo/`](demo/)** — the live-demo code: one piece of science (fitting an
Ornstein–Uhlenbeck process) run three ways.

| Script | What it does |
|---|---|
| `01_mcmc.py` + `01_run.sh` | One job, one realisation. Read this one first. |
| `02_inference.py` + `02_sweep.sh` | Array job: fit a hundred realisations, then check the error bars are honest. |
| `03_ensemble.py` + `03_sweep.sh` | Array job: simulate a hundred realisations, no fitting. |

Everything runs on a laptop too — Slurm is optional. See
[`demo/README.md`](demo/README.md) for setup and how to submit.

[`demo/CLAUDE.md`](demo/CLAUDE.md) is worth a look even if you never run the
code: it is the example from Part 2 of a context file that tells an agent the
cluster facts it cannot guess.

## Building the slides

```bash
make pdf      # slides.pdf
make watch    # live preview at localhost:8080
```

Needs `npx` (Node). Nothing else is required to read the talk.
