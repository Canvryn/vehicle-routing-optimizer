from __future__ import annotations

import argparse
import csv
from dataclasses import dataclass
from pathlib import Path
from time import perf_counter

try:
    from .distance import Location
    from .heuristic import Route, load_locations, solve_nearest_neighbor
    from .improve import improve_routes_with_two_opt
    from .savings import solve_clarke_wright_savings
    from .time_windows import build_default_time_windows, evaluate_route_timings, timing_summary
except ImportError:
    from distance import Location
    from heuristic import Route, load_locations, solve_nearest_neighbor
    from improve import improve_routes_with_two_opt
    from savings import solve_clarke_wright_savings
    from time_windows import build_default_time_windows, evaluate_route_timings, timing_summary


@dataclass(frozen=True)
class ScenarioResult:
    method: str
    vehicle_capacity: int
    route_count: int
    total_distance: float
    total_lateness: float
    late_stops: int
    on_time_rate: float
    objective_value: float
    total_demand: int
    average_utilization: float
    max_route_distance: float
    runtime_ms: float


def evaluate_capacity_scenario(
    locations: list[Location],
    vehicle_capacity: int,
    method: str = "nearest_neighbor",
    lateness_penalty: float = 10,
    speed: float = 1,
) -> tuple[ScenarioResult, list[Route]]:
    """Solve one capacity scenario and return route-level performance metrics."""

    construction_solvers = {
        "nearest_neighbor": solve_nearest_neighbor,
        "nearest_neighbor_2opt": solve_nearest_neighbor,
        "savings": solve_clarke_wright_savings,
        "savings_2opt": solve_clarke_wright_savings,
    }
    if method not in construction_solvers:
        raise ValueError(f"Unknown method: {method}")

    start = perf_counter()
    routes = construction_solvers[method](locations, vehicle_capacity=vehicle_capacity)
    if method.endswith("_2opt"):
        routes = improve_routes_with_two_opt(locations, routes)
    windows = build_default_time_windows(locations)
    timings = evaluate_route_timings(locations, routes, windows, speed=speed)
    time_summary = timing_summary(timings)
    runtime_ms = (perf_counter() - start) * 1000

    total_distance = sum(route.distance for route in routes)
    total_lateness = float(time_summary["total_lateness"])
    objective_value = total_distance + lateness_penalty * total_lateness
    total_demand = sum(location.demand for location in locations)
    available_capacity = max(len(routes) * vehicle_capacity, 1)
    average_utilization = total_demand / available_capacity
    max_route_distance = max((route.distance for route in routes), default=0)

    return (
        ScenarioResult(
            method=method,
            vehicle_capacity=vehicle_capacity,
            route_count=len(routes),
            total_distance=round(total_distance, 2),
            total_lateness=round(total_lateness, 2),
            late_stops=int(time_summary["late_stops"]),
            on_time_rate=float(time_summary["on_time_rate"]),
            objective_value=round(objective_value, 2),
            total_demand=total_demand,
            average_utilization=round(average_utilization, 4),
            max_route_distance=round(max_route_distance, 2),
            runtime_ms=round(runtime_ms, 3),
        ),
        routes,
    )


def run_capacity_scenarios(
    locations: list[Location],
    vehicle_capacities: list[int],
    methods: list[str] | None = None,
    lateness_penalty: float = 10,
    speed: float = 1,
) -> list[ScenarioResult]:
    """Compare routing methods across several vehicle capacities."""

    selected_methods = methods or ["nearest_neighbor"]
    return [
        evaluate_capacity_scenario(
            locations,
            capacity,
            method,
            lateness_penalty=lateness_penalty,
            speed=speed,
        )[0]
        for method in selected_methods
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
                "method",
                "vehicle_capacity",
                "route_count",
                "total_distance",
                "total_lateness",
                "late_stops",
                "on_time_rate",
                "objective_value",
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


def parse_methods(raw_methods: str) -> list[str]:
    methods = [value.strip() for value in raw_methods.split(",") if value.strip()]
    if not methods:
        raise ValueError("at least one method is required")
    return methods


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run VRP capacity scenarios.")
    parser.add_argument("--input", type=Path, default=Path("data/sample_customers.csv"))
    parser.add_argument("--capacities", default="25,30,40,50")
    parser.add_argument(
        "--methods",
        default="nearest_neighbor,nearest_neighbor_2opt,savings,savings_2opt",
    )
    parser.add_argument("--lateness-penalty", type=float, default=10)
    parser.add_argument("--speed", type=float, default=1)
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
    methods = parse_methods(args.methods)
    scenario_results = run_capacity_scenarios(
        locations,
        capacities,
        methods,
        lateness_penalty=args.lateness_penalty,
        speed=args.speed,
    )
    write_scenario_results(scenario_results, args.output)

    print(f"Wrote {len(scenario_results)} scenario results to {args.output}")
    for result in scenario_results:
        print(
            f"method={result.method}, "
            f"capacity={result.vehicle_capacity}, "
            f"routes={result.route_count}, "
            f"distance={result.total_distance:.2f}, "
            f"lateness={result.total_lateness:.2f}, "
            f"objective={result.objective_value:.2f}, "
            f"utilization={result.average_utilization:.2%}, "
            f"runtime_ms={result.runtime_ms:.3f}"
        )


if __name__ == "__main__":
    main()
