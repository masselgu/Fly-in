import heapq
from errors import ParserError
from graph import Graph
from zone import Zone


class Pathfinder:
    """Dijkstra-based pathfinding engine for drone routing."""

    def __init__(self, graph: Graph) -> None:
        """Initialize the routing engine with a navigation graph."""
        self.graph = graph

    def _movement_cost(self, zone: Zone) -> float:
        """Calculate traversal cost based on zone type."""
        if zone.zone_type == "restricted":
            return 2.0
        if zone.zone_type == "priority":
            return 0.9
        return 1.0

    def _initialize_costs(self, start: str) -> dict[str, float]:
        """Set up initial cost table with infinity for all zones."""
        costs: dict[str, float] = {}
        for name in self.graph.zones:
            costs[name] = float("inf")
        costs[start] = 0.0
        return costs

    def _initialize_previous(self) -> dict[str, str | None]:
        """Set up previous zone tracker for path reconstruction."""
        previous: dict[str, str | None] = {}
        for name in self.graph.zones:
            previous[name] = None
        return previous

    def _rebuild_route(self, previous: dict[str, str | None],
                       end: str) -> list[Zone]:
        """Reconstruct full route from end zone back to start."""
        route: list[Zone] = []
        current: str | None = end

        while current is not None:
            route.append(self.graph.zones[current])
            current = previous[current]

        route.reverse()
        return route

    def compute_route(self, start: str, end: str) -> list[Zone]:
        """
        Compute optimal route from start to end zone.

        Uses Dijkstra algorithm with priority queue for efficiency.
        Accounts for zone types and movement costs.
        Skips blocked zones automatically.

        Args:
            start: name of the departure zone
            end: name of the destination zone

        Returns:
            list of Zone objects representing the optimal path
        """
        if start not in self.graph.zones:
            raise ParserError(
                f"departure zone '{start}' does not exist in the map"
            )
        if end not in self.graph.zones:
            raise ParserError(
                f"destination zone '{end}' does not exist in the map"
            )
        if start == end:
            return [self.graph.zones[start]]

        costs = self._initialize_costs(start)
        previous = self._initialize_previous()
        visited: set[str] = set()

        # priority queue: (cost, zone_name)
        pq: list[tuple[float, str]] = []
        heapq.heappush(pq, (0.0, start))

        while pq:
            current_cost, current = heapq.heappop(pq)

            # skip already processed zones
            if current in visited:
                continue

            # destination reached!
            if current == end:
                break

            visited.add(current)

            for neighbor in self.graph.get_neighbors(current):

                # blocked zones are impassable
                if neighbor.zone_type == "blocked":
                    continue

                new_cost = current_cost + self._movement_cost(neighbor)

                if new_cost < costs[neighbor.name]:
                    costs[neighbor.name] = new_cost
                    previous[neighbor.name] = current
                    heapq.heappush(pq, (new_cost, neighbor.name))

        # no route exists
        if costs[end] == float("inf"):
            raise ParserError(
                f"navigation failed — no flyable route exists "
                f"between '{start}' and '{end}'"
            )

        return self._rebuild_route(previous, end)

    def compute_all_routes(self, start: str,
                           end: str,
                           nb_drones: int) -> list[list[Zone]]:
        routes: list[list[Zone]] = []
        primary = self.compute_route(start, end)

        for _ in range(nb_drones):
            routes.append(primary)

        return routes
