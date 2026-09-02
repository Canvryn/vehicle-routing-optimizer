from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path

try:
    from .distance import Location, build_distance_matrix
    from .heuristic import Route, format_route, load_locations, route_distance
except ImportError:
    from distance import Location, build_distance_matrix
    from heuristic import Route, format_route, load_locations, route_distance


@dataclass
class WorkingRoute:
    stops: list[Location]
    load: int

    @property
    def first_customer_id(self) -> str:
        return self.stops[0].location_id

    @property
    def last_customer_id(self) -> str:
        return self.stops[-1].location_id


def calculate_savings(
    depot: Location,
    customers: list[Location],
    matrix: dict[str, dict[str, float]],
) -> list[tuple[float, str, str]]:
    """Calculate Clarke-Wright savings for each pair of customers."""

    savings: list[tuple[float, str, str]] = []
    for first_index, first in enumerate(customers):
        for second in customers[first_index + 1 :]:
            saving = (
                matrix[depot.location_id][first.location_id]
                + matrix[depot.location_id][second.location_id]
                - matrix[first.location_id][second.location_id]
            )
            savings.append((saving, first.location_id, second.location_id))
    return sorted(savings, reverse=True)


def _find_route_containing(
    routes: list[WorkingRoute], customer_id: str
) -> WorkingRoute | None:
    for route in routes:
        if any(stop.location_id == customer_id for stop in route.stops):
            return route
    return None


def _try_merge_routes(
    first_route: WorkingRoute,
    second_route: WorkingRoute,
    first_customer_id: str,
    second_customer_id: str,
    vehicle_capacity: int,
) -> bool:
    """Merge two routes when the customer pair is on compatible route ends."""

    if first_route is second_route:
        return False
    if first_route.load + second_route.load > vehicle_capacity:
        return False

    if (
        first_route.last_customer_id == first_customer_id
        and second_route.first_customer_id == second_customer_id
    ):
        first_route.stops.extend(second_route.stops)
    elif (
        first_route.first_customer_id == first_customer_id
        and second_route.last_customer_id == second_customer_id
    ):
        first_route.stops = second_route.stops + first_route.stops
    elif (
        first_route.first_customer_id == first_customer_id
        and second_route.first_customer_id == second_customer_id
    ):
        first_route.stops = list(reversed(first_route.stops)) + second_route.stops
    elif (
        first_route.last_customer_id == first_customer_id
        and second_route.last_customer_id == second_customer_id
    ):
        first_route.stops.extend(reversed(second_route.stops))
    else:
        return False

    first_route.load += second_route.load
    return True


def solve_clarke_wright_savings(
    locations: list[Location], vehicle_capacity: int, depot_id: str = "DEPOT"
) -> list[Route]:
    """Build capacity-feasible routes with the Clarke-Wright savings heuristic."""

    if vehicle_capacity <= 0:
        raise ValueError("vehicle_capacity must be positive")

    depot = next(location for location in locations if location.location_id == depot_id)
    customers = [location for location in locations if location.location_id != depot_id]
    oversized = [customer for customer in customers if customer.demand > vehicle_capacity]
    if oversized:
        ids = ", ".join(customer.location_id for customer in oversized)
        raise ValueError(f"Customers exceed vehicle capacity: {ids}")

    matrix = build_distance_matrix(locations)
    working_routes = [
        WorkingRoute(stops=[customer], load=customer.demand) for customer in customers
    ]

    for _, first_customer_id, second_customer_id in calculate_savings(
        depot, customers, matrix
    ):
        first_route = _find_route_containing(working_routes, first_customer_id)
        second_route = _find_route_containing(working_routes, second_customer_id)
        if first_route is None or second_route is None:
            continue

        if _try_merge_routes(
            first_route,
            second_route,
            first_customer_id,
            second_customer_id,
            vehicle_capacity,
        ):
            working_routes.remove(second_route)

    routes: list[Route] = []
    for vehicle_id, working_route in enumerate(working_routes, start=1):
        stops = [depot, *working_route.stops, depot]
        routes.append(
            Route(
                vehicle_id=vehicle_id,
                stops=stops,
                load=working_route.load,
                distance=route_distance(stops, matrix),
            )
        )
    return routes


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run Clarke-Wright savings VRP.")
    parser.add_argument("--input", type=Path, default=Path("data/sample_customers.csv"))
    parser.add_argument("--vehicle-capacity", type=int, default=40)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    locations = load_locations(args.input)
    routes = solve_clarke_wright_savings(locations, args.vehicle_capacity)
    total_distance = sum(route.distance for route in routes)

    print(f"Built {len(routes)} routes")
    print(f"Total distance: {total_distance:.2f}")
    print()
    for route in routes:
        print(format_route(route))


if __name__ == "__main__":
    main()

