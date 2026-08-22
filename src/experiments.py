from __future__ import annotations

import argparse
import csv
from dataclasses import dataclass
from pathlib import Path
from time import perf_counter

try:
    from .distance import Location
    from .heuristic import Route, load_locations, solve_nearest_neighbor
except ImportError:
    from distance import Location
    from heuristic import Route, load_locations, solve_nearest_neighbor


@dataclass(frozen=True)
class ScenarioResult:
    vehicle_capacity: int
    route_count: int
    total_distance: float
    total_demand: int
    average_utilization: float
    max_route_distance: float
    runtime_ms: float


def evaluate_capacity_scenario(
    locations: list[Location], vehicle_capacity: int
) -> tuple[ScenarioResult, list[Route]]:
    """Solve one capacity scenario and return route-level performance metrics."""

    start = perf_counter()
    routes = solve_nearest_neighbor(locations, vehicle_capacity=vehicle_capacity)
    runtime_ms = (perf_counter() - start) * 1000

    total_distance = sum(route.distance for route in routes)
    total_demand = sum(location.demand for location in locations)
    available_capacity = max(len(routes) * vehicle_capacity, 1)
    average_utilization = total_demand / available_capacity
    max_route_distance = max((route.distance for route in routes), default=0)

    return (
        ScenarioResult(
            vehicle_capacity=vehicle_capacity,
            route_count=len(routes),
            total_distance=round(total_distance, 2),
            total_demand=total_demand,
            average_utilization=round(average_utilization, 4),
            max_route_distance=round(max_route_distance, 2),
            runtime_ms=round(runtime_ms, 3),
        ),
        routes,
    )


def run_capacity_scenarios(
    locations: list[Location], vehicle_capacities: list[int]
) -> list[ScenarioResult]:
    """Compare the baseline heuristic across several vehicle capacities."""

    return [
        evaluate_capacity_scenario(locations, capacity)[0]
        for capacity in vehicle_capacities
    ]


def write_scenario_results(
    scenario_results: list[ScenarioResult], output_path: Path
) -> None:
    """Write scenario comparison metrics to CSV."""

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=[
                "vehicle_capacity",
                "route_count",
                "total_distance",
                "total_demand",
                "average_utilization",
                "max_route_distance",
                "runtime_ms",
            ],
        )
        writer.writeheader()
        writer.writerows(result.__dict__ for result in scenario_results)


def parse_capacities(raw_capacities: str) -> list[int]:
    capacities = [int(value.strip()) for value in raw_capacities.split(",")]
    if any(capacity <= 0 for capacity in capacities):
        raise ValueError("all capacities must be positive")
    return capacities


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run baseline VRP capacity scenarios.")
    parser.add_argument("--input", type=Path, default=Path("data/sample_customers.csv"))
    parser.add_argument("--capacities", default="25,30,40,50")
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("results/scenario_comparison.csv"),
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    locations = load_locations(args.input)
    capacities = parse_capacities(args.capacities)
    scenario_results = run_capacity_scenarios(locations, capacities)
    write_scenario_results(scenario_results, args.output)

    print(f"Wrote {len(scenario_results)} scenario results to {args.output}")
    for result in scenario_results:
        print(
            f"capacity={result.vehicle_capacity}, "
            f"routes={result.route_count}, "
            f"distance={result.total_distance:.2f}, "
            f"utilization={result.average_utilization:.2%}, "
            f"runtime_ms={result.runtime_ms:.3f}"
        )


if __name__ == "__main__":
    main()
