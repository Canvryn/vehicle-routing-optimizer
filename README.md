# Vehicle Routing Optimizer

This project models a delivery routing problem as an operations research decision tool. Given a depot, a fleet of vehicles, customer locations, and customer demand, the goal is to assign deliveries to vehicle routes that minimize travel distance while satisfying capacity constraints.

The project includes a reproducible synthetic data generator, distance matrix utilities, a nearest-neighbor baseline heuristic, and a Clarke-Wright savings heuristic. Future versions will compare these heuristics against an optimization solver such as Google OR-Tools and extend the model with time windows, lateness penalties, and richer experiments.

## Why This Project Matters

Vehicle routing is a classic operations research problem with direct applications in logistics, supply chain planning, last-mile delivery, field service, and transportation analytics. This project is designed to show:

- mathematical modeling
- algorithmic thinking
- Python implementation
- clean experiment design
- practical business interpretation

## Current Features

- Generate reproducible synthetic delivery data.
- Represent a depot and customer locations in two-dimensional space.
- Assign each customer a delivery demand.
- Compute Euclidean distances between all locations.
- Build feasible vehicle routes using a nearest-neighbor heuristic.
- Build feasible vehicle routes using the Clarke-Wright savings heuristic.
- Improve route ordering with a 2-opt local search pass.
- Respect vehicle capacity constraints.
- Report total distance and route-level summaries.
- Export route summaries to CSV.
- Export a dependency-free SVG route map with route legend and demand labels.
- Compare routing outcomes across multiple vehicle-capacity scenarios.
- Validate route feasibility against depot, visit, load, and capacity constraints.
- Generate a Markdown experiment report from route and scenario outputs.

## Project Structure

```text
.
  README.md
  requirements.txt
  src/
    __init__.py
    distance.py
    generate_data.py
    heuristic.py
    savings.py
    improve.py
    experiments.py
    validate.py
    report.py
  data/
    sample_customers.csv
  results/
    route_map.svg
    route_summary.csv
    scenario_comparison.csv
    experiment_report.md
  tests/
    test_distance.py
    test_heuristic.py
```

## Mathematical Formulation

Let:

- `N` be the set of customers.
- `K` be the set of vehicles.
- `d_ij` be the distance from location `i` to location `j`.
- `q_i` be the demand of customer `i`.
- `Q` be the capacity of each vehicle.

The capacitated vehicle routing problem asks us to choose routes that minimize:

```text
sum of travel distances across all vehicles
```

subject to:

```text
each customer is visited exactly once
each route starts and ends at the depot
total demand on each vehicle route <= vehicle capacity
```

This repository starts with a heuristic solution method. A later version will add an exact or solver-based formulation for comparison.

## Quick Start

Install dependencies:

```bash
pip install -r requirements.txt
```

Generate sample data:

```bash
python src/generate_data.py --customers 20 --output data/sample_customers.csv
```

Run the baseline heuristic:

```bash
python src/heuristic.py --input data/sample_customers.csv --vehicle-capacity 40
```

Run the Clarke-Wright savings heuristic:

```bash
python src/savings.py --input data/sample_customers.csv --vehicle-capacity 40
```

Run savings plus 2-opt local search:

```bash
python src/improve.py --input data/sample_customers.csv --vehicle-capacity 40
```

Save route outputs:

```bash
python src/heuristic.py --input data/sample_customers.csv --vehicle-capacity 40 --summary-output results/route_summary.csv --map-output results/route_map.svg
```

Run capacity comparison experiments:

```bash
python src/experiments.py --input data/sample_customers.csv --capacities 25,30,40,50 --methods nearest_neighbor,nearest_neighbor_2opt,savings,savings_2opt --output results/scenario_comparison.csv
```

Validate the baseline routes:

```bash
python src/validate.py --input data/sample_customers.csv --vehicle-capacity 40
```

Generate the experiment report:

```bash
python src/report.py --scenarios results/scenario_comparison.csv --routes results/route_summary.csv --output results/experiment_report.md
```

Run tests:

```bash
python -m unittest discover -s tests
```

## Example Output

```text
Built 4 routes
Total distance: 463.72

Vehicle 1: load=38, distance=118.54, route=DEPOT -> C007 -> C003 -> C011 -> DEPOT
Vehicle 2: load=36, distance=102.19, route=DEPOT -> C014 -> C002 -> C018 -> DEPOT
```

Your exact output may differ when you generate a new data set.

## Roadmap

- Add route visualizations with Matplotlib.
- Add OR-Tools solver implementation.
- Compare heuristic and solver performance.
- Add time windows and lateness penalties.
- Create experiment scenarios for small, medium, and larger instances.
