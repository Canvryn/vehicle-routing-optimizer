from __future__ import annotations

import argparse
import csv
from dataclasses import asdict, dataclass
from pathlib import Path

try:
    from .experiments import parse_capacities, parse_methods, run_capacity_scenarios
    from .generate_data import SCENARIO_PRESETS, generate_preset_customers, write_customers
    from .heuristic import load_locations
except ImportError:
    from experiments import parse_capacities, parse_methods, run_capacity_scenarios
    from generate_data import SCENARIO_PRESETS, generate_preset_customers, write_customers
    from heuristic import load_locations


@dataclass(frozen=True)
class BenchmarkRow:
    scenario: str
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


def run_benchmarks(
    scenario_names: list[str],
    vehicle_capacities: list[int],
    methods: list[str],
    data_dir: Path,
    lateness_penalty: float = 10,
    speed: float = 1,
) -> list[BenchmarkRow]:
    """Generate named scenarios and evaluate routing methods on each one."""

    benchmark_rows: list[BenchmarkRow] = []
    for scenario_name in scenario_names:
        rows = generate_preset_customers(scenario_name)
        scenario_path = data_dir / f"{scenario_name}.csv"
        write_customers(rows, scenario_path)
        locations = load_locations(scenario_path)
        scenario_results = run_capacity_scenarios(
            locations,
            vehicle_capacities,
            methods,
            lateness_penalty=lateness_penalty,
            speed=speed,
        )

        for result in scenario_results:
            benchmark_rows.append(
                BenchmarkRow(
                    scenario=scenario_name,
                    method=result.method,
                    vehicle_capacity=result.vehicle_capacity,
                    route_count=result.route_count,
                    total_distance=result.total_distance,
                    total_lateness=result.total_lateness,
                    late_stops=result.late_stops,
                    on_time_rate=result.on_time_rate,
                    objective_value=result.objective_value,
                    total_demand=result.total_demand,
                    average_utilization=result.average_utilization,
                    max_route_distance=result.max_route_distance,
                    runtime_ms=result.runtime_ms,
                )
            )
    return benchmark_rows


def write_benchmark_summary(benchmark_rows: list[BenchmarkRow], output_path: Path) -> None:
    """Write combined benchmark results to CSV."""

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=[
                "scenario",
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
        writer.writerows(asdict(row) for row in benchmark_rows)


def parse_scenarios(raw_scenarios: str) -> list[str]:
    scenario_names = [value.strip() for value in raw_scenarios.split(",") if value.strip()]
    unknown_names = sorted(set(scenario_names) - set(SCENARIO_PRESETS))
    if unknown_names:
        valid_names = ", ".join(sorted(SCENARIO_PRESETS))
        raise ValueError(
            f"Unknown scenarios: {', '.join(unknown_names)}. Valid scenarios: {valid_names}"
        )
    if not scenario_names:
        raise ValueError("at least one scenario is required")
    return scenario_names


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run named VRP benchmark scenarios.")
    parser.add_argument(
        "--scenarios",
        default="small,medium,high_demand,sparse_region",
        help="Comma-separated named scenarios to run.",
    )
    parser.add_argument("--capacities", default="25,40,55")
    parser.add_argument(
        "--methods",
        default="nearest_neighbor,savings,savings_2opt",
    )
    parser.add_argument("--lateness-penalty", type=float, default=10)
    parser.add_argument("--speed", type=float, default=1)
    parser.add_argument("--data-dir", type=Path, default=Path("data/benchmarks"))
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("results/benchmark_summary.csv"),
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    scenario_names = parse_scenarios(args.scenarios)
    capacities = parse_capacities(args.capacities)
    methods = parse_methods(args.methods)
    benchmark_rows = run_benchmarks(
        scenario_names,
        capacities,
        methods,
        data_dir=args.data_dir,
        lateness_penalty=args.lateness_penalty,
        speed=args.speed,
    )
    write_benchmark_summary(benchmark_rows, args.output)
    print(f"Wrote {len(benchmark_rows)} benchmark rows to {args.output}")


if __name__ == "__main__":
    main()

