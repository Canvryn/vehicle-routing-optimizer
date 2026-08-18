from __future__ import annotations

import argparse
import csv
from dataclasses import dataclass
from pathlib import Path

try:
    from .distance import Location, build_distance_matrix
except ImportError:
    from distance import Location, build_distance_matrix


@dataclass(frozen=True)
class Route:
    vehicle_id: int
    stops: list[Location]
    load: int
    distance: float

    @property
    def stop_ids(self) -> list[str]:
        return [stop.location_id for stop in self.stops]


def load_locations(input_path: Path) -> list[Location]:
    """Load depot and customers from a CSV file."""

    with input_path.open(newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        return [
            Location(
                location_id=row["location_id"],
                x=float(row["x"]),
                y=float(row["y"]),
                demand=int(row["demand"]),
            )
            for row in reader
        ]


def route_distance(route: list[Location], matrix: dict[str, dict[str, float]]) -> float:
    """Calculate the total distance of a route that includes depot endpoints."""

    return sum(
        matrix[route[index].location_id][route[index + 1].location_id]
        for index in range(len(route) - 1)
    )


def solve_nearest_neighbor(
    locations: list[Location], vehicle_capacity: int, depot_id: str = "DEPOT"
) -> list[Route]:
    """Build capacity-feasible routes using a nearest-neighbor heuristic."""

    if vehicle_capacity <= 0:
        raise ValueError("vehicle_capacity must be positive")

    depot = next(location for location in locations if location.location_id == depot_id)
    customers = [location for location in locations if location.location_id != depot_id]
    oversized = [customer for customer in customers if customer.demand > vehicle_capacity]
    if oversized:
        ids = ", ".join(customer.location_id for customer in oversized)
        raise ValueError(f"Customers exceed vehicle capacity: {ids}")

    matrix = build_distance_matrix(locations)
    unvisited = {customer.location_id: customer for customer in customers}
    routes: list[Route] = []
    vehicle_id = 1

    while unvisited:
        current = depot
        load = 0
        stops = [depot]

        while True:
            feasible_customers = [
                customer
                for customer in unvisited.values()
                if load + customer.demand <= vehicle_capacity
            ]
            if not feasible_customers:
                break

            next_customer = min(
                feasible_customers,
                key=lambda customer: matrix[current.location_id][customer.location_id],
            )
            stops.append(next_customer)
            load += next_customer.demand
            current = next_customer
            del unvisited[next_customer.location_id]

        stops.append(depot)
        routes.append(
            Route(
                vehicle_id=vehicle_id,
                stops=stops,
                load=load,
                distance=route_distance(stops, matrix),
            )
        )
        vehicle_id += 1

    return routes


def format_route(route: Route) -> str:
    path = " -> ".join(route.stop_ids)
    return (
        f"Vehicle {route.vehicle_id}: "
        f"load={route.load}, distance={route.distance:.2f}, route={path}"
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run baseline nearest-neighbor VRP.")
    parser.add_argument("--input", type=Path, default=Path("data/sample_customers.csv"))
    parser.add_argument("--vehicle-capacity", type=int, default=40)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    locations = load_locations(args.input)
    routes = solve_nearest_neighbor(locations, args.vehicle_capacity)
    total_distance = sum(route.distance for route in routes)

    print(f"Built {len(routes)} routes")
    print(f"Total distance: {total_distance:.2f}")
    print()
    for route in routes:
        print(format_route(route))


if __name__ == "__main__":
    main()
