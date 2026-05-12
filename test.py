import heapq
from errors import GraphError
from graph import Graph
from zone import Zone


ZONE_PRIORITY = {
    "priority": 0,
    "normal": 1,
    "restricted": 2,
    "blocked": 3
}


class Pathfinder:
    def __init__(self, graph: Graph):
        self.graph = graph

    def _mouvement_costs(self, zone: Zone) -> float:
        if zone.zone_type == "restricted":
            return 2.0
        return 1.0

    def _initialistation_costs(self, start) -> dict[str, float]:
        costs = {}
        for zone in self.graph.zones:
            costs[zone] = float("inf")
        costs[start] = 0.0
        return costs

    def _initialisation_previous(self) -> dict[str, str | None]:
        previous = {}
        for zone in self.graph.zones:
            previous[zone] = None
        return previous

    def _rebuild_route(self, previous, end) -> list[Zone]:
        route = []
        current = end
        while current is not None:
            route.append(current)
            current = previous[current]
        route.reverse()
        return route

    def _compute_route(self, start, end) -> list[Zone]:
        if start not in self.graph.zones:
            raise GraphError("invalid start zone")
        if end not in self.graph.zones:
            raise GraphError("invalid end zone")
        if start == end:
            return [self.graph.zones[start]]

        costs = self._initialistation_costs(start)
        previous = self._initialisation_previous()
        visited = set()
        pq = []
        heapq.heappush(pq, (0.0,
                            ZONE_PRIORITY[self.graph.zones[start].zone_type],
                            start))
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
                new_cost = current_cost + self._mouvement_costs(neighbor)
                if new_cost < costs[neighbor.name]:
                    costs[neighbor.name] = new_cost
                    previous[neighbor.name] = current
                    heapq.heappush(pq, (new_cost,
                                        ZONE_PRIORITY[neighbor.zone_type],
                                        neighbor.name))
        if costs[end] == float("inf"):
            raise GraphError("no path found between start and end")
        return self._rebuild_route(previous, end)

    def _compute_k_route(self, start, end, k=5) -> list[list[Zone]]:
        routes = []
        used_connection = set()
        while len(routes) < k:
            original_connection = self.graph.connections[:]
            self.graph.connections = [
                c for c in self.graph.connections
                if (min(c.zone1.name, c.zone2.name),
                    max(c.zone1.name, c.zone2.name)) not in used_connection
            ]
            try:
                route = self._compute_route(start, end)
            except Exception:
                break
            finally:
                self.graph.connections = original_connection

            route = [z.name for z in route]
            if route not in [[r.name for r in r] for r in routes]:
                for i in range(len(route) - 1):
                    a = min(route[i].name, route[i + 1].name)
                    b = max(route[i].name, route[i + 1].name)
                    used_connection.add((a, b))
                routes.append(route)
        if not routes:
            raise GraphError("no path available")
        return routes
