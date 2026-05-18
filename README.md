*This project has been created as part of the 42 curriculum by masselgu*

# Fly-in

## Description

Fly-in is a drone routing simulation system. The goal is to move a fleet of drones from a start zone to an end zone through a network of connected zones, in the fewest possible simulation turns.

The system handles:
- Multiple drone routing across parallel paths
- Zone types: normal, restricted, priority, blocked
- Zone and connection capacity constraints
- 2-turn transit through restricted zones
- Colored terminal visual output based on zone colors defined in the map

## Instructions

### Requirements

- Python 3.10 or later
- Dependencies listed in `requirements.txt`:
  - `mypy` — static type checking
  - `flake8` — code style linting
  - `matplotlib` - matplotlib.colors for colors


### Install dependencies

```bash
make install
```

### Run the code

```bash
make run
```
or

```bash
python3 main.py <file.txt>
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

```
nb_drones: 5
start_hub: hub 0 0 [color=green]
end_hub: goal 10 10 [color=yellow]
hub: zone1 3 4 [zone=restricted color=red]
hub: zone2 6 2 [zone=priority max_drones=2]
hub: blocked 5 5 [zone=blocked]
connection: hub-zone1
connection: zone1-zone2 [max_link_capacity=2]
connection: zone2-goal
```

- `zone=` can be `normal`, `restricted`, `priority`, or `blocked`
- `max_drones=` sets how many drones can occupy a zone simultaneously (default 1)
- `max_link_capacity=` sets how many drones can cross a connection per turn (default 1)
- Comments start with `#`
- Zone names cannot contain dashes or spaces

## Algorithm

### Pathfinding — Dijkstra with connection-blocking diversification

The pathfinder uses **Dijkstra's algorithm** to find the shortest path from start to end. To discover multiple distinct routes, a connection-blocking heuristic is applied: after each path is found, the middle connections of that path are temporarily blocked and Dijkstra is run again, forcing it to find a different route. This continues until no more distinct paths exist.

Movement costs per zone type:
- `normal` → 1.0 turn
- `priority` → 1.0 turn (preferred via tiebreaker in the priority queue)
- `restricted` → 2.0 turns
- `blocked` → unreachable

Priority zones are preferred by assigning them a lower tiebreaker value in the heap tuple, so Dijkstra naturally picks them over normal zones when costs are equal.

Drones are assigned to paths using `drone_index % num_paths`, distributing them across all available routes for parallel routing.

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

- Dijkstra time: O(V × E) per call — connection list scan in `get_neighbors`
- Path diversification: O(P × V × E) where P is the number of distinct paths found
- Simulation per turn: O(D) where D is the number of active drones
- Simulation total: O(T × D) where T is total turns
- Space: O(V + E + D + T)

## Visual Representation

The terminal output uses `matplotlib.colors` for robust and consistent color handling.

- Only the **zone part** of each movement token (`D<ID>-<zone>`) is colored, while the drone identifier remains unchanged for clarity
- Colors are resolved using `matplotlib.colors`, allowing support for a wide range of standard and named colors
- Each zone color is defined in the map and consistently applied during the simulation
- If a color is invalid, an error is raised to enforce strict input validation

This design improves readability by clearly separating drone identifiers from destination zones, while ensuring that all visual elements strictly follow the map configuration.

Example input:
```
make run FILE=map.txt
```

Example output:
```
D1-junction  D2-junction
D1-path_a  D2-path_b  D3-junction  D4-junction
D1-goal  D2-goal  D3-path_a  D4-path_b
D3-goal  D4-goal

✓ 4 drone(s) delivered in 4 turn(s).
```

## Resources

- Dijkstra's algorithm visual: https://visualgo.net/en
- Graph representations: https://www.geeksforgeeks.org/dsa/graph-and-its-representations/
- Heap and priority queue: https://www.chrislaux.com


### AI Usage

- Used to generate additional test cases to validate edge cases
- Provided resources and references for understanding key concepts
- Helped identify useful documentation and learning materials
- Suggested external readings related to graphs, Dijkstra’s algorithm, and Python tooling

