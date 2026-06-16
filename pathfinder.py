import heapq
from typing import List, Dict, Tuple, Set
from errors import ParserError
from graph import Graph
from zone import Zone


ZONE_PRIORITY: Dict[str, int] = {
    "priority": 0,
    "normal": 1,
    "restricted": 2,
    "blocked": 3,
}


class Pathfinder:
    """Compute drone routes with Dijkstra-based pathfinding."""

    def __init__(self, graph: Graph) -> None:
        """Initialize the pathfinder.

        Args:
            graph: Graph object used for route computation.

        Returns:
            None.
        """
        self.graph = graph
        self.edge_penalty: Dict[Tuple[str, str], float] = {}

    def _conn_key(self, a: str, b: str) -> tuple[str, str]:
        """Return a canonical sorted key for a connection.

        Args:
            a: First zone name as a string.
            b: Second zone name as a string.

        Returns:
            Tuple of the two zone names sorted alphabetically.
        """
        return (min(a, b), max(a, b))

    def _movement_cost(self, zone: Zone) -> float:
        """Return the traversal cost of a zone.

        Args:
            zone: Destination Zone object.

        Returns:
            Float movement cost associated with the zone.
        """
        if zone.zone_type == "restricted":
            return 2.0
        return 1.0

    def _edge_cost(self, a: str, b: str, base: float) -> float:
        """Return the cost of traversing a connection.

        Args:
            a: Source zone name as a string.
            b: Destination zone name as a string.
            base: Float base movement cost.

        Returns:
            Float total connection cost including penalties.
        """
        return base + self.edge_penalty.get(self._conn_key(a, b), 0.0)

    def compute_route(self, start: str, end: str) -> List[Zone]:
        """Compute the shortest route between two zones.

        Args:
            start: Departure zone name as a string.
            end: Destination zone name as a string.

        Returns:
            Ordered list of Zone objects forming the route.

        Raises:
            ParserError: If a zone is missing or no valid route exists.
        """

        if start not in self.graph.zones:
            raise ParserError(f"start zone '{start}' not found")
        if end not in self.graph.zones:
            raise ParserError(f"end zone '{end}' not found")

        start_zone_type = self.graph.zones[start].zone_type
        pq: List[tuple[float, int, str]] = [(0.0,
                                            ZONE_PRIORITY[start_zone_type],
                                            start)]
        costs: Dict[str, float] = {z: float("inf") for z in self.graph.zones}
        previous: Dict[str, str | None] = {z: None for z in self.graph.zones}
        visited: Set[str] = set()
        costs[start] = 0.0

        while pq:
            cost, _, current = heapq.heappop(pq)

            if current in visited:
                continue
            visited.add(current)

            if current == end:
                break

            for neighbor in self.graph.get_neighbors(current):
                if neighbor.zone_type == "blocked":
                    continue

                base = self._movement_cost(neighbor)
                new_cost = cost + self._edge_cost(current, neighbor.name, base)

                if new_cost < costs[neighbor.name]:
                    costs[neighbor.name] = new_cost
                    previous[neighbor.name] = current
                    heapq.heappush(pq, (new_cost,
                                        ZONE_PRIORITY[neighbor.zone_type],
                                        neighbor.name))

        if costs[end] == float("inf"):
            raise ParserError(f"no route found between '{start}' and '{end}'")

        return self._rebuild_route(previous, end)

    def _rebuild_route(
        self,
        previous: Dict[str, str | None],
        end: str
    ) -> List[Zone]:
        """Rebuild a route from predecessor data.

        Args:
            previous: Dictionary mapping each zone name to its predecessor.
            end: Destination zone name as a string.

        Returns:
            Ordered list of Zone objects in the route.
        """
        path: List[Zone] = []
        current: str | None = end

        while current is not None:
            path.append(self.graph.zones[current])
            current = previous[current]

        path.reverse()
        return path

    def compute_k_routes(self, start: str, end: str) -> List[List[Zone]]:
        """Compute multiple alternative routes.

        Args:
            start: Departure zone name as a string.
            end: Destination zone name as a string.

        Returns:
            List of distinct routes, each as a list of Zone objects.

        Raises:
            ParserError: If no route exists.
        """

        routes: List[List[Zone]] = []

        for _ in range(10):
            try:
                route = self.compute_route(start, end)
            except ParserError:
                break

            route_names = [z.name for z in route]

            if route_names in [[z.name for z in r] for r in routes]:
                break

            routes.append(route)

            for i in range(len(route) - 1):
                a = route[i].name
                b = route[i + 1].name
                key = self._conn_key(a, b)
                self.edge_penalty[key] = self.edge_penalty.get(key, 0.0) + 3.0

        if not routes:
            raise ParserError(f"no route found between '{start}' and '{end}'")

        return routes
