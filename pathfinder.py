from errors import ParserError
from graph import Graph
from zone import Zone


class Pathfinder:
    """Dijkstra pathfinding algorithm for drone routing."""

    def __init__(self, graph: Graph) -> None:
        """Initialize pathfinder with a graph."""
        self.graph = graph

    def _get_cost(self, zone: Zone) -> int:
        """Return movement cost based on zone type."""
        if zone.zone_type == "restricted":
            return 2
        return 1

    def _get_cheapest(self, costs: dict[str, float],
                      visited: list[str]) -> str | None:
        """Return unvisited zone with lowest cost."""
        cheapest: str | None = None
        lowest: float = float("inf")
        for name, cost in costs.items():
            if name not in visited and cost < lowest:
                lowest = cost
                cheapest = name
        return cheapest

    def find_path(self, start: str, end: str) -> list[Zone]:
        """Find shortest path from start to end using Dijkstra."""
        if start not in self.graph.zones:
            raise ParserError(f"Zone '{start}' not found in graph!")
        if end not in self.graph.zones:
            raise ParserError(f"Zone '{end}' not found in graph!")

        # initialize costs to infinity for all zones
        costs: dict[str, float] = {}
        for name in self.graph.zones:
            costs[name] = float("inf")
        costs[start] = 0

        # track previous zone for path reconstruction
        previous: dict[str, str | None] = {}
        for name in self.graph.zones:
            previous[name] = None

        visited: list[str] = []

        while True:
            # get cheapest unvisited zone
            current = self._get_cheapest(costs, visited)

            # no reachable zones left
            if current is None:
                break

            # reached the end!
            if current == end:
                break

            visited.append(current)

            # check all neighbors
            for neighbor in self.graph.get_neighbors(current):

                # skip blocked zones
                if neighbor.zone_type == "blocked":
                    continue

                # calculate new cost
                new_cost = costs[current] + self._get_cost(neighbor)

                # update if cheaper path found
                if new_cost < costs[neighbor.name]:
                    costs[neighbor.name] = new_cost
                    previous[neighbor.name] = current

        # check if end was reached
        if costs[end] == float("inf"):
            raise ParserError(
                f"No path found from '{start}' to '{end}'!"
            )

        # rebuild path from end to start
        path: list[Zone] = []
        current_name: str | None = end

        while current_name is not None:
            path.append(self.graph.zones[current_name])
            current_name = previous[current_name]

        # reverse to get start → end order
        path.reverse()
        return path
