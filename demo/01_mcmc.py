#!/usr/bin/env python3
"""01 -- ONE realisation, ONE posterior. The single-job demo.

Simulate one Ornstein-Uhlenbeck realisation, then recover (theta, mu, sigma)
from it by MCMC and plot the posterior. Converges in a couple of seconds on
one core: get it right on your laptop first, then make it big on the cluster.

    python 01_mcmc.py                    # -> posterior.png

Because the data are synthetic we know the answer, so the corner plot has
something to be checked against: the red crosshairs should land inside the
contours. That is one realisation, though -- landing inside once tells you
almost nothing. Checking it properly is what 02 is for.
"""

import argparse
import time

import numpy as np
import matplotlib
matplotlib.use("Agg")            # no display on a compute node
import matplotlib.pyplot as plt
import corner

import ou


def main():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--task-id", type=int, default=0, help="which realisation")
    p.add_argument("--steps", type=int, default=4000, help="MCMC steps per walker")
    p.add_argument("--walkers", type=int, default=32, help="ensemble size")
    p.add_argument("--burn", type=int, default=500, help="MCMC steps discarded")
    p.add_argument("--out", default="posterior.png")
    args = p.parse_args()

    t0 = time.time()
    _, x = ou.simulate(args.task_id)
    chain, diag = ou.fit(x, walkers=args.walkers, steps=args.steps,
                         burn=args.burn, seed=args.task_id)
    s = ou.summarise(chain)
    wall = time.time() - t0

    # Health checks. Look at these before you look at the pretty picture.
    print(f"realisation {args.task_id}: {args.steps} steps in {wall:.1f} s")
    print(f"  acceptance {diag['acceptance']:.2f}   autocorr {diag['autocorr']:.0f}"
          f" steps  (want << {diag['usable']})")
    for name, truth, m, sd, pull in zip(ou.NAMES, ou.TRUTHS,
                                        s["post_mean"], s["post_sd"], s["pull"]):
        print(f"  {name:>5} = {m:6.3f} +/- {sd:5.3f}   truth {truth:5.3f}"
              f"   pull {pull:+5.2f}")

    fig = corner.corner(chain, labels=ou.LABELS, truths=list(ou.TRUTHS),
                        quantiles=[0.16, 0.5, 0.84], show_titles=True,
                        title_fmt=".3f", truth_color="#c44")
    fig.savefig(args.out, dpi=160)
    plt.close(fig)
    print(f"  wrote {args.out}")


if __name__ == "__main__":
    main()
