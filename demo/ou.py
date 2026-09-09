#!/usr/bin/env python3
"""The model. Imported by the numbered scripts; not run on its own.

The Ornstein-Uhlenbeck process -- the canonical noisy relaxation. A quantity
is pulled back towards a mean at rate theta and kicked by white noise of
amplitude sigma:

    dx = theta * (mu - x) dt + sigma dW

Started from a known x0, the state is exactly Gaussian at every later time:

    <x(t)>   = mu + (x0 - mu) * exp(-theta t)
    Var x(t) = sigma^2 / (2 theta) * (1 - exp(-2 theta t))

so the ensemble fans out from x0 and settles into a stationary band.

Two consequences make this a good demo. The simulation is exact -- the step
below is the true transition density, not Euler-Maruyama -- and so is the
likelihood. Simulation and inference use the same three lines of algebra,
and there is no discretisation error to argue about.
"""

import numpy as np
import emcee

# The process. Every task uses these same values -- only the noise differs.
TRUTH = dict(theta=0.5, mu=1.0, sigma=0.5)
X0 = 3.0                         # common initial condition, away from mu
DT = 0.05                        # observation cadence
N_STEPS = 4000                   # so T = 200 = 100 relaxation times

NAMES = ("theta", "mu", "sigma")
LABELS = [r"$\theta$", r"$\mu$", r"$\sigma$"]
TRUTHS = np.array([TRUTH[n] for n in NAMES])


def simulate(task_id, theta=None, mu=None, sigma=None,
             x0=X0, dt=DT, n=N_STEPS):
    """One realisation. The task id IS the realisation: it seeds the RNG."""
    theta = TRUTH["theta"] if theta is None else theta
    mu = TRUTH["mu"] if mu is None else mu
    sigma = TRUTH["sigma"] if sigma is None else sigma

    rng = np.random.default_rng(task_id)
    a = np.exp(-theta * dt)
    s = sigma * np.sqrt((1.0 - a * a) / (2.0 * theta))
    kicks = rng.normal(scale=s, size=n)

    x = np.empty(n + 1)
    x[0] = x0
    for i in range(n):
        x[i + 1] = mu + a * (x[i] - mu) + kicks[i]
    return np.arange(n + 1) * dt, x


def envelope(t, theta=None, mu=None, sigma=None, x0=X0):
    """Analytic mean and standard deviation of the ensemble at time t."""
    theta = TRUTH["theta"] if theta is None else theta
    mu = TRUTH["mu"] if mu is None else mu
    sigma = TRUTH["sigma"] if sigma is None else sigma
    mean = mu + (x0 - mu) * np.exp(-theta * t)
    var = sigma**2 / (2.0 * theta) * (1.0 - np.exp(-2.0 * theta * t))
    return mean, np.sqrt(var)


def log_prob(params, x_prev, x_next, dt):
    """log posterior, conditional on x0. Flat priors, hard edges."""
    theta, mu, sigma = params
    if not (0.0 < theta < 10.0 and -10.0 < mu < 10.0 and 0.0 < sigma < 5.0):
        return -np.inf
    a = np.exp(-theta * dt)
    var = sigma**2 * (1.0 - a * a) / (2.0 * theta)
    resid = x_next - (mu + a * (x_prev - mu))
    return -0.5 * np.sum(resid**2 / var + np.log(2.0 * np.pi * var))


def moment_estimate(x, dt=DT):
    """Method of moments: a cheap, decent starting point for the walkers."""
    mu = x.mean()
    d = x - mu
    a = np.clip(np.sum(d[1:] * d[:-1]) / np.sum(d * d), 1e-6, 1 - 1e-6)
    theta = -np.log(a) / dt
    return np.array([theta, mu, np.sqrt(2.0 * theta * d.var())])


def fit(x, dt=DT, walkers=32, steps=4000, burn=500, seed=0):
    """Recover (theta, mu, sigma) from one realisation. Returns a flat chain.

    Walkers start in a tight ball around the method-of-moments estimate. A
    bad starting point is the commonest reason an MCMC "does not work".
    """
    rng = np.random.default_rng(seed)
    start = moment_estimate(x, dt) * (1.0 + 1e-3 * rng.normal(size=(walkers, 3)))
    sampler = emcee.EnsembleSampler(walkers, 3, log_prob, args=(x[:-1], x[1:], dt))
    sampler.run_mcmc(start, steps, progress=False)
    diagnostics = dict(acceptance=float(np.mean(sampler.acceptance_fraction)),
                       autocorr=float(np.max(sampler.get_autocorr_time(quiet=True))),
                       usable=steps - burn)
    return sampler.get_chain(discard=burn, thin=10, flat=True), diagnostics


def summarise(chain):
    """Posterior mean, sd, pull against the truth, and 68% coverage."""
    mean = chain.mean(axis=0)
    sd = chain.std(axis=0)
    lo, hi = np.percentile(chain, [16, 84], axis=0)
    return dict(post_mean=mean, post_sd=sd,
                pull=(mean - TRUTHS) / sd,          # should be a unit Gaussian
                inside68=(lo < TRUTHS) & (TRUTHS < hi))
