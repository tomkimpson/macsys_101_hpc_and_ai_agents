#!/usr/bin/env python3
"""02 -- MCMC on many datasets. An array job over INFERENCES.

Task i fits realisation i, exactly as 01 does, and saves the summary. The
expensive thing here is the fit -- a few seconds each, and it would be hours
if the model were a real one -- so the tasks go to the cluster, not a loop.

    python 02_inference.py --task-id 7 --out results/fit_007.npz
    python 02_inference.py --collate --out inference.png

Why bother running it a hundred times? Because one posterior cannot tell you
whether your error bars are right. A hundred can: if they are honest, the
pull

    (posterior mean - truth) / posterior sd

is a unit Gaussian, and the truth sits inside the 68% credible interval 68%
of the time. This is the check you want after anyone -- an agent included --
has edited your likelihood.
"""

import argparse
import glob
import time

import numpy as np
import matplotlib
matplotlib.use("Agg")            # no display on a compute node
import matplotlib.pyplot as plt

import ou


def run_task(args):
    """One array task: simulate realisation i, fit it, save the summary."""
    t0 = time.time()
    _, x = ou.simulate(args.task_id)
    chain, diag = ou.fit(x, walkers=args.walkers, steps=args.steps,
                         burn=args.burn, seed=args.task_id)
    s = ou.summarise(chain)
    wall = time.time() - t0

    print(f"realisation {args.task_id}: fitted in {wall:.1f} s"
          f"   acceptance {diag['acceptance']:.2f}"
          f"   autocorr {diag['autocorr']:.0f}")
    for name, truth, m, sd, pull in zip(ou.NAMES, ou.TRUTHS,
                                        s["post_mean"], s["post_sd"], s["pull"]):
        print(f"  {name:>5} = {m:6.3f} +/- {sd:5.3f}   truth {truth:5.3f}"
              f"   pull {pull:+5.2f}")

    if args.out:
        np.savez(args.out, task_id=args.task_id, truths=ou.TRUTHS,
                 wall=wall, **s)
        print(f"  wrote {args.out}")


def collate(args):
    """Gather every task and ask whether the error bars are honest."""
    files = sorted(glob.glob(f"{args.results}/fit_*.npz"))
    if not files:
        raise SystemExit(f"no fits in {args.results}/ -- did the array run?")
    d = [np.load(f) for f in files]
    n = len(d)

    pull = np.array([x["pull"] for x in d])              # (n, 3)
    inside = np.array([x["inside68"] for x in d])        # (n, 3)
    print(f"collated {n} fits, {np.sum([x['wall'] for x in d]):.0f} s of CPU")
    for i, name in enumerate(ou.NAMES):
        print(f"  {name:>5}: pull mean {pull[:, i].mean():+.2f}"
              f"  sd {pull[:, i].std():.2f}"
              f"  68% coverage {100 * inside[:, i].mean():.0f}%")

    fig, ax = plt.subplots(figsize=(5.8, 3.9), constrained_layout=True)
    ax.hist(pull.ravel(), bins=22, range=(-4, 4), density=True,
            color="#356", alpha=0.65, label=f"{n} fits $\\times$ 3 parameters")
    z = np.linspace(-4, 4, 200)
    ax.plot(z, np.exp(-0.5 * z**2) / np.sqrt(2 * np.pi), color="#c44", lw=1.8,
            label="unit Gaussian")
    ax.set_xlabel(r"pull  $(\hat{p} - p_{\rm true})\,/\,\sigma_p$")
    ax.set_ylabel("density")
    ax.set_title(f"ensemble of inference: {100 * inside.mean():.0f}% inside 68%")
    ax.legend(frameon=False, fontsize=9)
    fig.savefig(args.out, dpi=160)
    print(f"  wrote {args.out}")


def main():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--task-id", type=int, default=0,
                   help="SLURM_ARRAY_TASK_ID; picks the realisation to fit")
    p.add_argument("--steps", type=int, default=4000, help="MCMC steps per walker")
    p.add_argument("--walkers", type=int, default=32, help="ensemble size")
    p.add_argument("--burn", type=int, default=500, help="MCMC steps discarded")
    p.add_argument("--collate", action="store_true",
                   help="gather results/fit_*.npz and make the figure instead")
    p.add_argument("--results", default="results", help="directory of .npz files")
    p.add_argument("--out", default=None)
    args = p.parse_args()

    if args.collate:
        args.out = args.out or "inference.png"
        collate(args)
    else:
        run_task(args)


if __name__ == "__main__":
    main()
