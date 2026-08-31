from __future__ import annotations

import argparse
import csv
from pathlib import Path


def load_csv_rows(input_path: Path) -> list[dict[str, str]]:
    """Load CSV rows as dictionaries."""

    with input_path.open(newline="", encoding="utf-8") as file:
        return list(csv.DictReader(file))


def find_lowest_distance_scenario(
    scenario_rows: list[dict[str, str]]
) -> dict[str, str]:
    """Return the scenario with the lowest total distance."""

    if not scenario_rows:
        raise ValueError("scenario_rows must not be empty")
    return min(scenario_rows, key=lambda row: float(row["total_distance"]))


def find_fewest_route_scenario(scenario_rows: list[dict[str, str]]) -> dict[str, str]:
    """Return the scenario using the fewest vehicle routes."""

    if not scenario_rows:
        raise ValueError("scenario_rows must not be empty")
    return min(
        scenario_rows,
        key=lambda row: (int(row["route_count"]), float(row["total_distance"])),
    )


def markdown_table(rows: list[dict[str, str]], columns: list[str]) -> str:
    """Render selected CSV columns as a Markdown table."""

    header = "| " + " | ".join(columns) + " |"
    separator = "| " + " | ".join("---" for _ in columns) + " |"
    body = [
        "| " + " | ".join(str(row[column]) for column in columns) + " |"
        for row in rows
    ]
    return "\n".join([header, separator, *body])


def build_experiment_report(
    scenario_rows: list[dict[str, str]], route_rows: list[dict[str, str]]
) -> str:
    """Build a Markdown report from scenario and route outputs."""

    best_distance = find_lowest_distance_scenario(scenario_rows)
    fewest_routes = find_fewest_route_scenario(scenario_rows)
    route_count = len(route_rows)
    total_route_distance = sum(float(row["distance"]) for row in route_rows)
    total_route_load = sum(int(row["load"]) for row in route_rows)

    scenario_columns = [
        "vehicle_capacity",
        "route_count",
        "total_distance",
        "average_utilization",
        "runtime_ms",
    ]
    route_columns = ["vehicle_id", "customer_count", "load", "distance", "route"]

    return "\n".join(
        [
            "# Vehicle Routing Experiment Report",
            "",
            "## Summary",
            "",
            f"- Baseline route plan uses {route_count} routes.",
            f"- Baseline route plan travels {total_route_distance:.2f} distance units.",
            f"- Baseline route plan serves {total_route_load} units of demand.",
            f"- Lowest-distance capacity scenario: capacity {best_distance['vehicle_capacity']} with total distance {best_distance['total_distance']}.",
            f"- Fewest-route capacity scenario: capacity {fewest_routes['vehicle_capacity']} using {fewest_routes['route_count']} routes.",
            "",
            "## Scenario Comparison",
            "",
            markdown_table(scenario_rows, scenario_columns),
            "",
            "## Baseline Routes",
            "",
            markdown_table(route_rows, route_columns),
            "",
            "## Interpretation",
            "",
            "Increasing vehicle capacity generally reduces the number of routes, but the nearest-neighbor heuristic can still produce non-monotonic distance changes because early greedy choices affect later routing options. This motivates comparing the baseline against a solver-based optimization model in a future phase.",
            "",
        ]
    )


def write_experiment_report(
    scenario_input: Path, routes_input: Path, output_path: Path
) -> None:
    """Load result CSVs and write a Markdown experiment report."""

    scenario_rows = load_csv_rows(scenario_input)
    route_rows = load_csv_rows(routes_input)
    report = build_experiment_report(scenario_rows, route_rows)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(report, encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate a VRP experiment report.")
    parser.add_argument(
        "--scenarios",
        type=Path,
        default=Path("results/scenario_comparison.csv"),
    )
    parser.add_argument(
        "--routes",
        type=Path,
        default=Path("results/route_summary.csv"),
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("results/experiment_report.md"),
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    write_experiment_report(args.scenarios, args.routes, args.output)
    print(f"Wrote experiment report to {args.output}")


if __name__ == "__main__":
    main()

