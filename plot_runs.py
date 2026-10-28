#!/usr/bin/env python3
"""plot_runs.py: plot one or more Anasazi model runs against the historical data.

Usage (run from inside the model folder):
    python3 plot_runs.py outputs/harvest.adj_*.csv -o harvest_sweep.png
    python3 plot_runs.py outputs/harvest.adj_*.csv --title "Effect of harvest.adj"

Each CSV must have the year in the first column and the number of households
in the second (this is what NumberOfHousehold.csv contains). Header lines are
skipped automatically. The historical line comes from data/target_data.csv.
"""
import argparse
import csv
import os
import sys

import matplotlib
matplotlib.use("Agg")  # save to file, no screen needed
import matplotlib.pyplot as plt


def read_series(path):
    """Return (years, values) from the first two numeric columns of a CSV."""
    years, values = [], []
    with open(path, newline="") as f:
        for row in csv.reader(f):
            if len(row) < 2:
                continue
            try:
                y = float(row[0])
                v = float(row[1])
            except ValueError:
                continue  # header or junk line
            if not (800 <= y <= 1350):
                continue  # ignore junk rows outside the simulation period
            years.append(y)
            values.append(v)
    return years, values


def label_from_filename(path):
    """outputs/harvest.adj_0.62.csv -> 'harvest.adj = 0.62'."""
    stem = os.path.basename(path)
    if stem.endswith(".csv"):
        stem = stem[:-4]
    if "_" in stem:
        name, value = stem.rsplit("_", 1)
        return f"{name} = {value}"
    return stem


def sort_key(path):
    """Sort runs by their numeric value when the filename has one."""
    try:
        return float(label_from_filename(path).split("= ")[-1])
    except ValueError:
        return float("inf")


def main():
    p = argparse.ArgumentParser(description="Plot model runs vs historical data")
    p.add_argument("runs", nargs="+", help="CSV files from model runs")
    p.add_argument("--target", default="data/target_data.csv",
                   help="historical data CSV (default: data/target_data.csv)")
    p.add_argument("-o", "--output", default="sweep.png", help="output image")
    p.add_argument("--title", default=None, help="chart title")
    args = p.parse_args()

    fig, ax = plt.subplots(figsize=(10, 5.5))

    if os.path.exists(args.target):
        ty, tv = read_series(args.target)
        ax.plot(ty, tv, color="black", linewidth=2.5, label="Historical (target_data.csv)")
    else:
        print(f"Warning: {args.target} not found, plotting runs only.", file=sys.stderr)

    for path in sorted(args.runs, key=sort_key):
        years, values = read_series(path)
        if not years:
            print(f"Warning: no data in {path}, skipped.", file=sys.stderr)
            continue
        ax.plot(years, values, linewidth=1.4, label=label_from_filename(path))
        print(f"{path}: peak {max(values):.0f} households in {years[values.index(max(values))]:.0f}, "
              f"final {values[-1]:.0f} in {years[-1]:.0f}")

    ax.set_xlabel("Year (AD)")
    ax.set_ylabel("Number of households")
    ax.set_title(args.title or "Anasazi model: simulated vs historical households")
    ax.grid(alpha=0.3)
    ax.legend()
    fig.tight_layout()
    fig.savefig(args.output, dpi=150)
    print(f"Saved {args.output}")


if __name__ == "__main__":
    main()
