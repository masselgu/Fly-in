*This project has been created as part of the 42 curriculum by masselgu*

# Fly-in

## Description

Fly-in is a drone routing simulation system. The goal is to move a fleet of drones
from a start zone to an end zone through a network of connected zones, in the fewest
possible simulation turns.

The system handles:
- Multiple drone routing across parallel paths
- Zone types: normal, restricted, priority, blocked
- Zone and connection capacity constraints
- 2-turn transit through restricted zones
- Colored terminal visual output

## Instructions

### Install dependencies

```bash
make install
```

### Run the simulation

```bash
make run
```

This runs the simulation on `map.txt` by default. To use a custom map:

```bash
python3 main.py my_map.txt
```

### Lint

```bash
make lint
```

### Debug

```bash
make debug
```

### Clean

```bash
make clean
```

## Map Format
nb_drones: 5
start_hub: hub 0 0 [color=green]
end_hub: goal 10 10 [color=yellow]
hub: zone1 3 4 [zone=restricted color=red]
hub: zone2 6 2 [zone=priority max_drones=2]
hub: blocked 5 5 [zone=blocked]
connection: hub-zone1
connection: zone1-zone2 [max_link_capacity=2]
connection: zone2-goal

- `zone=` can be `normal`, `restricted`, `priority`, or `blocked`
- `max_drones=` sets how many drones can occupy a zone simultaneously (default 1)
- `max_link_capacity=` sets how many drones can cross a connection per turn (default 1)
- Comments start with `#`

## Algorithm

### Pathfinding — Yen's k-shortest paths

The pathfinder uses **Dijkstra's algorithm** as its base, extended with **Yen's
k-shortest paths algorithm** to find up to 5 distinct routes from start to end.

Movement costs per zone type:
- `normal` → 1.0
- `priority` → 0.9 (preferred)
- `restricted` → 2.0 (costs 2 turns)
- `blocked` → unreachable

Paths are sorted by total cost so drones are assigned to the cheapest routes first.
Drones cycle across all available paths using `drone_index % num_paths`, ensuring
parallel routing when multiple paths exist.

### Simulation — turn-by-turn scheduling

Each turn the simulation:
1. Collects all drone movement candidates
2. Checks zone and connection capacity before committing any move
3. Tracks `leaving` and `entering` counts per zone to allow same-turn capacity sharing
4. Executes all valid moves simultaneously
5. Handles restricted zones with a 2-turn transit state on the drone

Special rules respected:
- Start zone accepts all drones simultaneously
- End zone accepts unlimited arrivals
- A drone in transit through a restricted zone must complete its move the next turn

### Complexity

- Dijkstra: O((V + E) log V) per call
- Yen's k-shortest: O(k * V * (V + E) log V)
- Simulation per turn: O(D) where D is the number of active drones
- Paths are computed once and cached — no recalculation during simulation

## Visual Representation

The terminal output uses `colorama` for colored display:
- Each drone has a consistent color across all turns (magenta, blue, cyan, green, yellow)
- Zone names are shown in cyan
- A summary line at the end shows total turns and drones delivered

Example output:
Turn   1: D1-middle  D2-middle
Turn   2: D1-goal    D2-goal
✓ All 2 drone(s) delivered in 2 turn(s).

## Resources

- Dijkstra's algorithm: https://en.wikipedia.org/wiki/Dijkstra%27s_algorithm
- Yen's k-shortest paths: https://en.wikipedia.org/wiki/Yen%27s_k-shortest_path_algorithm
- Python heapq: https://docs.python.org/3/library/heapq.html
- colorama: https://pypi.org/project/colorama/
- Python type hints: https://docs.python.org/3/library/typing.html
- flake8: https://flake8.pycqa.org/
- mypy: https://mypy.readthedocs.io/

### AI Usage

Claude (Anthropic) was used during this project for:
- Identifying and fixing bugs in the simulation capacity logic
- Implementing Yen's k-shortest paths algorithm
- Writing the `visual.py` colored terminal output
- Generating test map files to cover edge cases
- Explaining algorithm complexity and design tradeoffs

All AI-generated code was reviewed, tested, and understood before being included.