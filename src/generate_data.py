from __future__ import annotations

import argparse
import csv
import random
from pathlib import Path


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


def write_customers(rows: list[dict[str, str | int | float]], output_path: Path) -> None:
    """Write generated routing data to CSV."""

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=["location_id", "x", "y", "demand"])
        writer.writeheader()
        writer.writerows(rows)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate synthetic VRP customer data.")
    parser.add_argument("--customers", type=int, default=20)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--output", type=Path, default=Path("data/sample_customers.csv"))
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    rows = generate_customers(customer_count=args.customers, seed=args.seed)
    write_customers(rows, args.output)
    print(f"Wrote {len(rows) - 1} customers plus depot to {args.output}")


if __name__ == "__main__":
    main()

