# Vehicle Routing Experiment Report

## Summary

- Baseline route plan uses 3 routes.
- Baseline route plan travels 518.77 distance units.
- Baseline route plan serves 93 units of demand.
- Lowest-distance capacity scenario: capacity 50 with total distance 431.08.
- Fewest-route capacity scenario: capacity 50 using 2 routes.
- Best lateness-aware objective: savings at capacity 25 with objective 574.23.

## Scenario Comparison

| method | vehicle_capacity | route_count | total_distance | total_lateness | late_stops | objective_value | average_utilization | runtime_ms |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| nearest_neighbor | 25 | 4 | 685.02 | 44.98 | 3 | 1134.82 | 0.93 | 1.434 |
| nearest_neighbor | 30 | 4 | 716.31 | 194.81 | 5 | 2664.41 | 0.775 | 1.523 |
| nearest_neighbor | 40 | 3 | 518.77 | 215.54 | 6 | 2674.17 | 0.775 | 1.24 |
| nearest_neighbor | 50 | 2 | 474.83 | 540.93 | 10 | 5884.13 | 0.93 | 1.175 |
| nearest_neighbor_2opt | 25 | 4 | 670.88 | 84.35 | 1 | 1514.38 | 0.93 | 2.431 |
| nearest_neighbor_2opt | 30 | 4 | 675.14 | 168.9 | 3 | 2364.14 | 0.775 | 2.292 |
| nearest_neighbor_2opt | 40 | 3 | 505.74 | 300.3 | 5 | 3508.74 | 0.775 | 2.272 |
| nearest_neighbor_2opt | 50 | 2 | 450.31 | 564.71 | 10 | 6097.41 | 0.93 | 3.048 |
| savings | 25 | 4 | 535.53 | 3.87 | 1 | 574.23 | 0.93 | 3.715 |
| savings | 30 | 4 | 511.08 | 42.7 | 3 | 938.08 | 0.775 | 3.955 |
| savings | 40 | 3 | 445.25 | 41.76 | 3 | 862.85 | 0.775 | 3.267 |
| savings | 50 | 2 | 431.08 | 664.5 | 10 | 7076.08 | 0.93 | 4.187 |
| savings_2opt | 25 | 4 | 535.53 | 3.87 | 1 | 574.23 | 0.93 | 5.775 |
| savings_2opt | 30 | 4 | 511.08 | 42.7 | 3 | 938.08 | 0.775 | 5.795 |
| savings_2opt | 40 | 3 | 445.25 | 41.76 | 3 | 862.85 | 0.775 | 4.12 |
| savings_2opt | 50 | 2 | 431.08 | 664.5 | 10 | 7076.08 | 0.93 | 4.605 |

## Baseline Routes

| vehicle_id | customer_count | load | distance | route |
| --- | --- | --- | --- | --- |
| 1 | 9 | 40 | 209.36 | DEPOT -> C007 -> C005 -> C020 -> C010 -> C006 -> C012 -> C003 -> C017 -> C013 -> DEPOT |
| 2 | 9 | 37 | 185.47 | DEPOT -> C019 -> C009 -> C018 -> C015 -> C008 -> C016 -> C001 -> C004 -> C002 -> DEPOT |
| 3 | 2 | 16 | 123.94 | DEPOT -> C014 -> C011 -> DEPOT |

## Interpretation

Increasing vehicle capacity generally reduces the number of routes, but route quality depends on the tradeoff between travel distance and delivery lateness. The lateness-aware objective adds a penalty for missed time windows, which makes the scenario comparison closer to a real delivery-planning decision. This creates a stronger benchmark for a future solver-based optimization model.
