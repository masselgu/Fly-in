import heapq
from errors import ParserError
from graph import Graph
from zone import Zone
from typing import List, Dict


ZONE_PRIORITY: Dict[str, int] = {
    "priority":   0,
    "normal":     1,
    "restricted": 2,
    "blocked":    3,
}


class Pathfinder:
    """Dijkstra-based pathfinding engine for drone routing."""

    def __init__(self, graph: Graph) -> None:
        """Initialize the routing engine with a navigation graph."""
        self.graph = graph

    def _movement_cost(self, zone: Zone) -> float:
        """Calculate traversal cost based on zone type."""
        if zone.zone_type == "restricted":
            return 2.0
        return 1.0

    def _initialize_costs(self, start: str) -> Dict[str, float]:
        """Set up initial cost table with infinity for all zones."""
        costs: Dict[str, float] = {}
        for name in self.graph.zones:
            costs[name] = float("inf")
        costs[start] = 0.0
        return costs

    def _initialize_previous(self) -> Dict[str, str | None]:
        """Set up previous zone tracker for path reconstruction."""
        previous: Dict[str, str | None] = {}
        for name in self.graph.zones:
            previous[name] = None
        return previous

    def _rebuild_route(self, previous: Dict[str, str | None],
                       end: str) -> List[Zone]:
        """Reconstruct full route from end zone back to start."""
        route: List[Zone] = []
        current: str | None = end

        while current is not None:
            route.append(self.graph.zones[current])
            current = previous[current]

        route.reverse()
        return route

    def compute_route(self, start: str, end: str) -> List[Zone]:
        """Compute the single shortest path from start to end."""
        if start not in self.graph.zones:
            raise ParserError(
                f"departure zone '{start}' does not exist in the map"
            )
        if end not in self.graph.zones:
            raise ParserError(
                f"destination zone '{end}' does not exist in the map"
            )

        costs = self._initialize_costs(start)
        previous = self._initialize_previous()
        visited: set[str] = set()

        start_zone = self.graph.zones[start]
        pq: List[tuple[float, int, str]] = []
        heapq.heappush(pq, (0.0, ZONE_PRIORITY[start_zone.zone_type], start))

        while pq:
            current_cost, _, current = heapq.heappop(pq)

            if current in visited:
                continue

            if current == end:
                break

            visited.add(current)

            for neighbor in self.graph.get_neighbors(current):
                if neighbor.zone_type == "blocked":
                    continue

                new_cost = current_cost + self._movement_cost(neighbor)

                if new_cost < costs[neighbor.name]:
                    costs[neighbor.name] = new_cost
                    previous[neighbor.name] = current
                    heapq.heappush(
                        pq,
                        (new_cost, ZONE_PRIORITY[neighbor.zone_type],
                         neighbor.name)
                    )

        if costs[end] == float("inf"):
            raise ParserError(
                f"navigation failed — no flyable route exists "
                f"between '{start}' and '{end}'"
            )

        return self._rebuild_route(previous, end)

    def compute_k_routes(self, start: str, end: str,
                         k: int = 5) -> List[List[Zone]]:
        """Compute k disjoint routes by blocking already-used connections."""
        routes: List[List[Zone]] = []
        used_connections: set[tuple[str, str]] = set()

        while len(routes) < k:
            original_connections = self.graph.connections[:]
            self.graph.connections = [
                c for c in self.graph.connections
                if (min(c.zone1.name, c.zone2.name),
                    max(c.zone1.name, c.zone2.name)) not in used_connections
            ]

            try:
                route = self.compute_route(start, end)
            except Exception:
                break
            finally:
                self.graph.connections = original_connections

            route_names = [z.name for z in route]
            if route_names not in [[z.name for z in r] for r in routes]:
                for i in range(len(route) - 1):
                    if route[i].name == start or \
                     route[i + 1].name == end:
                        continue
                    a = min(route[i].name, route[i + 1].name)
                    b = max(route[i].name, route[i + 1].name)
                    used_connections.add((a, b))
                routes.append(route)
            else:
                break

        if not routes:
            raise ParserError(
                f"no route found between '{start}' and '{end}'"
            )

        return routes
