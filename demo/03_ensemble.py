#!/usr/bin/env python3
"""03 -- many forward simulations. An array job over REALISATIONS.

No fitting here. Task i simulates realisation i and saves the trajectory.
Collating them gives the spread of the process, checked against the analytic
envelope -- the shape of an ensemble weather forecast, for the same reason.

    python 03_ensemble.py --task-id 7 --out results/sim_007.npz
    python 03_ensemble.py --collate --out ensemble.png

Honest caveat: THIS forward model is cheap -- milliseconds -- so on a laptop
you would just loop. It is laid out as an array because that is the structure
that survives contact with a real forward model. An operational weather
centre runs a ~50-member ensemble as ~50 independent integrations precisely
because one member is hours of compute. Same shape, different price tag.
"""

import argparse
import time

import numpy as np
import matplotlib
matplotlib.use("Agg")            # no display on a compute node
import matplotlib.pyplot as plt

import ou

T_MAX = 40.0                     # how much of the trajectory to plot
THIN = 5                         # keep every 5th sample on disk


def run_task(args):
    """One array task: simulate realisation i and save the trajectory."""
    t0 = time.time()
    t, x = ou.simulate(args.task_id)
    wall = time.time() - t0

    print(f"realisation {args.task_id}: {len(x)} steps in {wall * 1e3:.0f} ms"
          f"   mean {x.mean():.3f}   final {x[-1]:.3f}")

    if args.out:
        # Thin before writing: the collated figure does not need every step,
        # and 100 tasks x 4000 points is a lot of disk for nothing.
        np.savez(args.out, task_id=args.task_id, t=t[::THIN], x=x[::THIN],
                 wall=wall)
        print(f"  wrote {args.out}")


def collate(args):
    """Gather every realisation and compare the spread with the analytics."""
    import glob
    files = sorted(glob.glob(f"{args.results}/sim_*.npz"))
    if not files:
        raise SystemExit(f"no sims in {args.results}/ -- did the array run?")
    d = [np.load(f) for f in files]
    n = len(d)

    

    t = d[0]["t"]
    xs = np.array([x["x"] for x in d])                   # (n, len(t))
    mean, sd = ou.envelope(t)

    # Does the ensemble actually match the analytics? Check, do not eyeball.
    late = t > 20.0
    print(f"collated {n} realisations")
    print(f"  stationary mean  sim {xs[:, late].mean():.3f}"
          f"   analytic {mean[late][0]:.3f}")
    print(f"  stationary sd    sim {xs[:, late].std():.3f}"
          f"   analytic {sd[late][0]:.3f}")

    fig, ax = plt.subplots(figsize=(5.8, 3.9), constrained_layout=True)
    for x in xs:
        ax.plot(t, x, color="#356", lw=0.4, alpha=0.25)
    ax.plot(t, mean, color="#c44", lw=1.8, label="analytic mean")
    for k, ls in ((1, "-"), (2, "--")):
        ax.plot(t, mean + k * sd, ls, color="#c44", lw=1.2,
                label=rf"$\pm{k}\sigma$")
        ax.plot(t, mean - k * sd, ls, color="#c44", lw=1.2)
    ax.set_xlim(0, T_MAX)
    ax.set_xlabel("time")
    ax.set_ylabel("$x$")
    ax.set_title(f"ensemble of realisations: {n} runs, one process")
    ax.legend(frameon=False, loc="upper right", fontsize=9)
    fig.savefig(args.out, dpi=160)
    print(f"  wrote {args.out}")


def main():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--task-id", type=int, default=0,
                   help="SLURM_ARRAY_TASK_ID; picks the noise realisation")
    p.add_argument("--collate", action="store_true",
                   help="gather results/sim_*.npz and make the figure instead")
    p.add_argument("--results", default="results", help="directory of .npz files")
    p.add_argument("--out", default=None)
    args = p.parse_args()

    if args.collate:
        args.out = args.out or "ensemble.png"
        collate(args)
    else:
        run_task(args)


if __name__ == "__main__":
    main()
