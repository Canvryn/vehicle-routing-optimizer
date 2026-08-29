from __future__ import annotations

import argparse
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

try:
    from .distance import Location
    from .heuristic import Route, load_locations, solve_nearest_neighbor
except ImportError:
    from distance import Location
    from heuristic import Route, load_locations, solve_nearest_neighbor


@dataclass(frozen=True)
class FeasibilityViolation:
    rule: str
    message: str


@dataclass(frozen=True)
class FeasibilityReport:
    is_feasible: bool
    route_count: int
    customer_count: int
    total_visited_customers: int
    total_load: int
    violations: list[FeasibilityViolation]


def validate_routes(
    locations: list[Location],
    routes: list[Route],
    vehicle_capacity: int,
    depot_id: str = "DEPOT",
) -> FeasibilityReport:
    """Validate route output against basic capacitated VRP constraints."""

    location_by_id = {location.location_id: location for location in locations}
    customer_ids = {
        location.location_id
        for location in locations
        if location.location_id != depot_id
    }
    visited_customer_ids: list[str] = []
    violations: list[FeasibilityViolation] = []

    if depot_id not in location_by_id:
        violations.append(
            FeasibilityViolation("depot", f"Depot {depot_id} is missing from locations.")
        )

    for route in routes:
        if not route.stops:
            violations.append(
                FeasibilityViolation(
                    "route_structure",
                    f"Vehicle {route.vehicle_id} has no stops.",
                )
            )
            continue

        first_stop = route.stops[0].location_id
        last_stop = route.stops[-1].location_id
        if first_stop != depot_id or last_stop != depot_id:
            violations.append(
                FeasibilityViolation(
                    "depot_return",
                    f"Vehicle {route.vehicle_id} must start and end at {depot_id}.",
                )
            )

        computed_load = sum(stop.demand for stop in route.stops if stop.location_id != depot_id)
        if computed_load != route.load:
            violations.append(
                FeasibilityViolation(
                    "load_accounting",
                    f"Vehicle {route.vehicle_id} reports load {route.load}, but stops sum to {computed_load}.",
                )
            )

        if route.load > vehicle_capacity:
            violations.append(
                FeasibilityViolation(
                    "capacity",
                    f"Vehicle {route.vehicle_id} load {route.load} exceeds capacity {vehicle_capacity}.",
                )
            )

        for stop in route.stops:
            if stop.location_id == depot_id:
                continue
            if stop.location_id not in customer_ids:
                violations.append(
                    FeasibilityViolation(
                        "unknown_customer",
                        f"Vehicle {route.vehicle_id} visits unknown customer {stop.location_id}.",
                    )
                )
            visited_customer_ids.append(stop.location_id)

    visit_counts = Counter(visited_customer_ids)
    missing_customers = sorted(customer_ids - set(visited_customer_ids))
    duplicate_customers = sorted(
        customer_id for customer_id, count in visit_counts.items() if count > 1
    )

    if missing_customers:
        violations.append(
            FeasibilityViolation(
                "missing_customer",
                f"Missing customers: {', '.join(missing_customers)}.",
            )
        )

    if duplicate_customers:
        violations.append(
            FeasibilityViolation(
                "duplicate_customer",
                f"Customers visited more than once: {', '.join(duplicate_customers)}.",
            )
        )

    return FeasibilityReport(
        is_feasible=not violations,
        route_count=len(routes),
        customer_count=len(customer_ids),
        total_visited_customers=len(visited_customer_ids),
        total_load=sum(route.load for route in routes),
        violations=violations,
    )


def format_feasibility_report(report: FeasibilityReport) -> str:
    """Format a feasibility report for command-line output."""

    status = "feasible" if report.is_feasible else "infeasible"
    lines = [
        f"Solution status: {status}",
        f"Routes: {report.route_count}",
        f"Customers: {report.customer_count}",
        f"Visited customers: {report.total_visited_customers}",
        f"Total load: {report.total_load}",
    ]
    if report.violations:
        lines.append("")
        lines.append("Violations:")
        for violation in report.violations:
            lines.append(f"- {violation.rule}: {violation.message}")
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate baseline VRP routes.")
    parser.add_argument("--input", type=Path, default=Path("data/sample_customers.csv"))
    parser.add_argument("--vehicle-capacity", type=int, default=40)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    locations = load_locations(args.input)
    routes = solve_nearest_neighbor(locations, vehicle_capacity=args.vehicle_capacity)
    report = validate_routes(locations, routes, vehicle_capacity=args.vehicle_capacity)
    print(format_feasibility_report(report))


if __name__ == "__main__":
    main()

