from __future__ import annotations

import argparse
import csv
import random
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ScenarioPreset:
    customer_count: int
    seed: int
    region_size: int
    min_demand: int
    max_demand: int


SCENARIO_PRESETS = {
    "small": ScenarioPreset(10, 7, 80, 1, 8),
    "medium": ScenarioPreset(30, 42, 100, 1, 10),
    "large": ScenarioPreset(75, 99, 140, 1, 12),
    "high_demand": ScenarioPreset(30, 123, 100, 6, 18),
    "sparse_region": ScenarioPreset(35, 202, 220, 1, 10),
    "tight_windows": ScenarioPreset(30, 314, 100, 1, 10),
}


def generate_customers(
    customer_count: int,
    seed: int = 42,
    region_size: int = 100,
    min_demand: int = 1,
    max_demand: int = 10,
) -> list[dict[str, str | int | float]]:
    """Generate a depot and synthetic customers for a routing instance."""

    rng = random.Random(seed)
    midpoint = region_size / 2
    rows: list[dict[str, str | int | float]] = [
        {
            "location_id": "DEPOT",
            "x": midpoint,
            "y": midpoint,
            "demand": 0,
        }
    ]

    for index in range(1, customer_count + 1):
        rows.append(
            {
                "location_id": f"C{index:03d}",
                "x": round(rng.uniform(0, region_size), 2),
                "y": round(rng.uniform(0, region_size), 2),
                "demand": rng.randint(min_demand, max_demand),
            }
        )
    return rows


def generate_preset_customers(
    preset_name: str,
) -> list[dict[str, str | int | float]]:
    """Generate customers from a named benchmark scenario preset."""

    if preset_name not in SCENARIO_PRESETS:
        valid_names = ", ".join(sorted(SCENARIO_PRESETS))
        raise ValueError(f"Unknown scenario preset: {preset_name}. Valid presets: {valid_names}")

    preset = SCENARIO_PRESETS[preset_name]
    return generate_customers(
        customer_count=preset.customer_count,
        seed=preset.seed,
        region_size=preset.region_size,
        min_demand=preset.min_demand,
        max_demand=preset.max_demand,
    )


def write_customers(rows: list[dict[str, str | int | float]], output_path: Path) -> None:
    """Write generated routing data to CSV."""

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=["location_id", "x", "y", "demand"])
        writer.writeheader()
        writer.writerows(rows)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate synthetic VRP customer data.")
    parser.add_argument(
        "--scenario",
        choices=sorted(SCENARIO_PRESETS),
        help="Named benchmark preset. Overrides individual generation settings.",
    )
    parser.add_argument("--customers", type=int, default=20)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--region-size", type=int, default=100)
    parser.add_argument("--min-demand", type=int, default=1)
    parser.add_argument("--max-demand", type=int, default=10)
    parser.add_argument("--output", type=Path, default=Path("data/sample_customers.csv"))
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.scenario:
        rows = generate_preset_customers(args.scenario)
    else:
        rows = generate_customers(
            customer_count=args.customers,
            seed=args.seed,
            region_size=args.region_size,
            min_demand=args.min_demand,
            max_demand=args.max_demand,
        )
    write_customers(rows, args.output)
    print(f"Wrote {len(rows) - 1} customers plus depot to {args.output}")


if __name__ == "__main__":
    main()
