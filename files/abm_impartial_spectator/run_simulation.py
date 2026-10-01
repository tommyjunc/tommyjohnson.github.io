#!/usr/bin/env python3
"""Run the impartial-spectator model and save its time series as CSV."""

import argparse
import csv
from pathlib import Path

if __package__:
    from .model import ImpartialSpectatorModel
else:
    from model import ImpartialSpectatorModel


def parse_args():
    parser = argparse.ArgumentParser(
        description="Simulate Rate My Professor-style reputation dynamics."
    )
    parser.add_argument(
        "--steps", type=int, default=50, help="number of update rounds"
    )
    parser.add_argument(
        "--students", type=int, default=100, help="number of students"
    )
    parser.add_argument(
        "--professors", type=int, default=5, help="number of professors"
    )
    parser.add_argument(
        "--conformity",
        type=float,
        default=0.25,
        help="student pull toward the current aggregate rating (0–1)",
    )
    parser.add_argument(
        "--adaptation-rate",
        type=float,
        default=0.1,
        help="professor behavior adjustment rate (0–1)",
    )
    parser.add_argument(
        "--noise",
        type=float,
        default=0.35,
        help="standard deviation of rating noise",
    )
    parser.add_argument("--seed", type=int, default=42, help="random seed")
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("results.csv"),
        help="output CSV path",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    if args.steps < 0:
        raise SystemExit("--steps must be non-negative")

    model = ImpartialSpectatorModel(
        n_students=args.students,
        n_professors=args.professors,
        conformity=args.conformity,
        adaptation_rate=args.adaptation_rate,
        noise=args.noise,
        seed=args.seed,
    )
    for _ in range(args.steps):
        model.step()

    collected = model.datacollector.get_model_vars_dataframe()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(
            [
                "step",
                "professor_id",
                "aggregate_rating",
                "behavior",
                "latent_quality",
                "internalized_spectator",
            ]
        )
        for step, record in collected.iterrows():
            for professor in model.professors:
                professor_id = professor.professor_id
                writer.writerow(
                    [
                        step,
                        professor_id,
                        record[f"professor_{professor_id}_aggregate_rating"],
                        record[f"professor_{professor_id}_behavior"],
                        record[f"professor_{professor_id}_latent_quality"],
                        record[f"professor_{professor_id}_internalized_spectator"],
                    ]
                )
    print(f"Wrote {len(collected) * len(model.professors)} rows to {args.output}")


if __name__ == "__main__":
    main()
