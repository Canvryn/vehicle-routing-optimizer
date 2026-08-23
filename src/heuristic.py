from __future__ import annotations

import argparse
import csv
from dataclasses import dataclass
from html import escape
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


def route_summary_rows(routes: list[Route]) -> list[dict[str, str | int | float]]:
    """Create flat route summaries that can be written to CSV."""

    return [
        {
            "vehicle_id": route.vehicle_id,
            "customer_count": len([stop for stop in route.stops if stop.demand > 0]),
            "load": route.load,
            "distance": round(route.distance, 2),
            "route": " -> ".join(route.stop_ids),
        }
        for route in routes
    ]


def write_route_summary(routes: list[Route], output_path: Path) -> None:
    """Write route-level performance metrics to CSV."""

    output_path.parent.mkdir(parents=True, exist_ok=True)
    rows = route_summary_rows(routes)
    with output_path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=["vehicle_id", "customer_count", "load", "distance", "route"],
        )
        writer.writeheader()
        writer.writerows(rows)


def write_route_map_svg(
    locations: list[Location],
    routes: list[Route],
    output_path: Path,
    width: int = 900,
    height: int = 650,
    padding: int = 50,
) -> None:
    """Write a dependency-free SVG map of the route plan."""

    min_x = min(location.x for location in locations)
    max_x = max(location.x for location in locations)
    min_y = min(location.y for location in locations)
    max_y = max(location.y for location in locations)
    x_range = max(max_x - min_x, 1)
    y_range = max(max_y - min_y, 1)

    def project(location: Location) -> tuple[float, float]:
        x = padding + ((location.x - min_x) / x_range) * (width - 2 * padding)
        y = height - padding - ((location.y - min_y) / y_range) * (height - 2 * padding)
        return x, y

    colors = [
        "#2563eb",
        "#dc2626",
        "#16a34a",
        "#9333ea",
        "#ea580c",
        "#0891b2",
        "#be123c",
        "#4f46e5",
    ]
    total_distance = sum(route.distance for route in routes)
    total_demand = sum(location.demand for location in locations)
    route_count = len(routes)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    elements = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="#f8fafc"/>',
        '<rect x="18" y="16" width="360" height="92" fill="#ffffff" stroke="#cbd5e1" stroke-width="1"/>',
        '<text x="36" y="46" font-family="Arial" font-size="22" font-weight="700" fill="#0f172a">Vehicle Routing Baseline</text>',
        f'<text x="36" y="72" font-family="Arial" font-size="13" fill="#475569">Routes: {route_count} | Demand: {total_demand} | Distance: {total_distance:.2f}</text>',
        '<text x="36" y="94" font-family="Arial" font-size="12" fill="#64748b">Nearest-neighbor heuristic with vehicle capacity constraints</text>',
        f'<rect x="{width - 250}" y="24" width="220" height="{44 + 24 * max(route_count, 1)}" fill="#ffffff" stroke="#cbd5e1" stroke-width="1"/>',
        f'<text x="{width - 230}" y="51" font-family="Arial" font-size="15" font-weight="700" fill="#0f172a">Route Legend</text>',
    ]

    for route in routes:
        color = colors[(route.vehicle_id - 1) % len(colors)]
        points = " ".join(
            f"{x:.1f},{y:.1f}" for x, y in (project(stop) for stop in route.stops)
        )
        elements.append(
            f'<polyline points="{points}" fill="none" stroke="{color}" stroke-width="3" stroke-linejoin="round" stroke-linecap="round" opacity="0.82"/>'
        )
        legend_y = 78 + 24 * (route.vehicle_id - 1)
        elements.append(
            f'<line x1="{width - 230}" y1="{legend_y}" x2="{width - 204}" y2="{legend_y}" stroke="{color}" stroke-width="4" stroke-linecap="round"/>'
        )
        elements.append(
            f'<text x="{width - 194}" y="{legend_y + 4}" font-family="Arial" font-size="12" fill="#334155">Vehicle {route.vehicle_id}: load {route.load}, dist {route.distance:.1f}</text>'
        )

    for location in locations:
        x, y = project(location)
        label = escape(location.location_id)
        if location.location_id == "DEPOT":
            elements.append(
                f'<rect x="{x - 8:.1f}" y="{y - 8:.1f}" width="16" height="16" fill="#111827"/>'
            )
            elements.append(
                f'<text x="{x + 12:.1f}" y="{y - 10:.1f}" font-family="Arial" font-size="13" font-weight="700" fill="#111827">{label}</text>'
            )
        else:
            elements.append(
                f'<circle cx="{x:.1f}" cy="{y:.1f}" r="5" fill="#ffffff" stroke="#334155" stroke-width="2"/>'
            )
            elements.append(
                f'<text x="{x + 7:.1f}" y="{y - 7:.1f}" font-family="Arial" font-size="10" fill="#334155">{label} d={location.demand}</text>'
            )

    elements.append("</svg>")
    output_path.write_text("\n".join(elements), encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run baseline nearest-neighbor VRP.")
    parser.add_argument("--input", type=Path, default=Path("data/sample_customers.csv"))
    parser.add_argument("--vehicle-capacity", type=int, default=40)
    parser.add_argument("--summary-output", type=Path)
    parser.add_argument("--map-output", type=Path)
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

    if args.summary_output:
        write_route_summary(routes, args.summary_output)
        print(f"\nWrote route summary to {args.summary_output}")

    if args.map_output:
        write_route_map_svg(locations, routes, args.map_output)
        print(f"Wrote route map to {args.map_output}")


if __name__ == "__main__":
    main()
