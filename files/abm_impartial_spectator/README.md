# Impartial Spectator Agent-Based Model

This standalone Mesa simulation explores how student judgments can become a
shared reputation signal and how professors may internalize and respond to it.
It is self-contained under `files/abm_impartial_spectator/` and does not affect
the Jekyll site.

## Setup

Python 3.9 or newer is required. From this directory, create an environment and
install the scoped dependencies:

```sh
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

On Windows, activate the environment with `.venv\Scripts\activate`.

## Run

From this directory:

```sh
python run_simulation.py --steps 50 --students 100 --professors 5 --seed 42
```

The command writes `results.csv` in the current directory by default. Choose a
different path with `--output`, for example:

```sh
python run_simulation.py --steps 100 --students 250 --professors 8 \
  --conformity 0.4 --adaptation-rate 0.15 --noise 0.5 \
  --seed 7 --output output/reputation.csv
```

It can also be run as a module from the repository root:

```sh
python -m files.abm_impartial_spectator.run_simulation --steps 20
```

## Parameters and dynamics

- `--steps`: number of update rounds (default: `50`; zero writes initial state).
- `--students`: students who each rate every professor each round (default: `100`).
- `--professors`: number of simulated professors (default: `5`).
- `--conformity`: weight from `0` to `1` pulling student evaluations toward the
  professor's current platform aggregate (default: `0.25`).
- `--adaptation-rate`: weight from `0` to `1` for professor behavior's movement
  toward its internalized spectator signal (default: `0.1`).
- `--noise`: non-negative standard deviation of student rating noise (default:
  `0.35`).
- `--seed`: random seed for reproducible runs (default: `42`).
- `--output`: CSV destination (default: `results.csv`).

Students combine latent quality and current behavior with individual bias and
random noise, then optionally conform toward the visible rating. The platform
updates its score as an exponential moving average of the current round's
ratings (a fixed smoothing weight of `0.25`). Professors internalize the public
signal with the same smoothing weight and adjust behavior toward it at the
configured adaptation rate. Scores, behavior, and latent quality are on a 1–5
scale.

The CSV is in long format, with one row per professor per step (including the
initial state at step 0). It contains `step`, `professor_id`,
`aggregate_rating`, `behavior`, `latent_quality`, and `internalized_spectator`.
