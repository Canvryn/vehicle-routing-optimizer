from __future__ import annotations

import argparse
import csv
from dataclasses import dataclass
from pathlib import Path

try:
    from .distance import Location, build_distance_matrix
    from .heuristic import Route, load_locations
    from .savings import solve_clarke_wright_savings
except ImportError:
    from distance import Location, build_distance_matrix
    from heuristic import Route, load_locations
    from savings import solve_clarke_wright_savings


@dataclass(frozen=True)
class TimeWindow:
    location_id: str
    earliest: float
    latest: float
    service_time: float = 0


@dataclass(frozen=True)
class StopTiming:
    vehicle_id: int
    location_id: str
    arrival_time: float
    service_start_time: float
    departure_time: float
    earliest: float
    latest: float
    waiting_time: float
    lateness: float


def build_default_time_windows(
    locations: list[Location],
    service_time: float = 5,
    customer_window_width: float = 120,
) -> dict[str, TimeWindow]:
    """Create deterministic time windows from customer location order."""

    windows: dict[str, TimeWindow] = {}
    customer_index = 0
    for location in locations:
        if location.location_id == "DEPOT":
            windows[location.location_id] = TimeWindow(
                location_id=location.location_id,
                earliest=0,
                latest=10_000,
                service_time=0,
            )
            continue

        customer_index += 1
        earliest = 30 + 10 * (customer_index % 6)
        windows[location.location_id] = TimeWindow(
            location_id=location.location_id,
            earliest=earliest,
            latest=earliest + customer_window_width,
            service_time=service_time,
        )
    return windows


def evaluate_route_timings(
    locations: list[Location],
    routes: list[Route],
    time_windows: dict[str, TimeWindow],
    speed: float = 1,
) -> list[StopTiming]:
    """Evaluate arrivals, waiting time, and lateness for each route stop."""

    if speed <= 0:
        raise ValueError("speed must be positive")

    matrix = build_distance_matrix(locations)
    timings: list[StopTiming] = []

    for route in routes:
        current_time = 0.0
        for index, stop in enumerate(route.stops):
            if index > 0:
                previous = route.stops[index - 1]
                current_time += matrix[previous.location_id][stop.location_id] / speed

            window = time_windows[stop.location_id]
            service_start = max(current_time, window.earliest)
            waiting_time = max(0.0, window.earliest - current_time)
            lateness = max(0.0, service_start - window.latest)
            departure_time = service_start + window.service_time

            timings.append(
                StopTiming(
                    vehicle_id=route.vehicle_id,
                    location_id=stop.location_id,
                    arrival_time=round(current_time, 2),
                    service_start_time=round(service_start, 2),
                    departure_time=round(departure_time, 2),
                    earliest=window.earliest,
                    latest=window.latest,
                    waiting_time=round(waiting_time, 2),
                    lateness=round(lateness, 2),
                )
            )
            current_time = departure_time

    return timings


def timing_summary(timings: list[StopTiming]) -> dict[str, float | int]:
    """Summarize route timing performance."""

    customer_timings = [timing for timing in timings if timing.location_id != "DEPOT"]
    late_stops = [timing for timing in customer_timings if timing.lateness > 0]
    total_lateness = sum(timing.lateness for timing in customer_timings)
    total_waiting_time = sum(timing.waiting_time for timing in customer_timings)
    on_time_rate = (
        (len(customer_timings) - len(late_stops)) / len(customer_timings)
        if customer_timings
        else 1.0
    )

    return {
        "customer_stops": len(customer_timings),
        "late_stops": len(late_stops),
        "total_lateness": round(total_lateness, 2),
        "total_waiting_time": round(total_waiting_time, 2),
        "on_time_rate": round(on_time_rate, 4),
    }


def write_timing_report(timings: list[StopTiming], output_path: Path) -> None:
    """Write stop-level timing results to CSV."""

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=[
                "vehicle_id",
                "location_id",
                "arrival_time",
                "service_start_time",
                "departure_time",
                "earliest",
                "latest",
                "waiting_time",
                "lateness",
            ],
        )
        writer.writeheader()
        writer.writerows(timing.__dict__ for timing in timings)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Evaluate route time windows.")
    parser.add_argument("--input", type=Path, default=Path("data/sample_customers.csv"))
    parser.add_argument("--vehicle-capacity", type=int, default=40)
    parser.add_argument("--speed", type=float, default=1)
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("results/time_window_report.csv"),
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    locations = load_locations(args.input)
    routes = solve_clarke_wright_savings(locations, args.vehicle_capacity)
    windows = build_default_time_windows(locations)
    timings = evaluate_route_timings(locations, routes, windows, speed=args.speed)
    summary = timing_summary(timings)
    write_timing_report(timings, args.output)

    print(f"Wrote stop timing report to {args.output}")
    print(
        "On-time rate: "
        f"{summary['on_time_rate']:.2%}; "
        f"late stops: {summary['late_stops']}; "
        f"total lateness: {summary['total_lateness']}"
    )


if __name__ == "__main__":
    main()

