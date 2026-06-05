from graph import Graph
from zone import Zone
import heapq
from errors import ParserError

zone_type = {
    "normal":     0,
    "priority":   1,
    "restricted": 2,
    "blocked":    3
    }


class Pathfinder:
    def __init__(self, graph: Graph) -> None:
        self.graph = graph

    def _inialisation_cost(self, start) -> dict:
        costs = {}
        for zone in self.graph.zones:
            costs[zone] = float("inf")
        costs[start] = 0.0
        return costs

    def _inialisation_previous(self) -> dict:
        previous = {}
        for zone in self.graph.zones:
            previous[zone] = None
        return previous

    def _do_mouvement(self, zone: Zone) -> float:
        if zone.zone_type == "restricted":
            return 2.0
        return 1.0

    def _rebuild_route(self, privious: dict, end: str) -> list[Zone]:
        current = end
        route = []
        while current is not None:
            route.append(self.graph.zones[current])
            current = privious[current]
        return route.reverse()

    def _compute_route(self, start: str, end: str) -> list[Zone]:
        if start not in self.graph.zones:
            raise ParserError("start not defined")
        if end not in self.graph.zones:
            raise ParserError("end not defined")

        costs = self._inialisation_cost(start)
        privious = self._inialisation_previous()
        visited = set()
        start_zone = self.graph.zones[start]

        pq = []
        heapq.heappush(pq, (costs[start], zone_type[start_zone.zone_type],
                            start))

        while pq:
            current_costs, _, current = heapq.heappop(pq)
            if current == end:
                break
            if current in visited:
                continue
            visited.add(current)
            for negibor in self.graph.get_neighbors(current):
                if negibor.zone_type == "blocked":
                    continue
                new_cost = current_costs + \
                    self._do_mouvement(negibor.zone_type)
                if new_cost < costs[negibor.name]:
                    costs[negibor.name] = new_cost
                    privious[negibor.name] = current
                    heapq.heappush(pq, (new_cost, zone_type[negibor.zone_type],
                                        negibor.name))

        if costs[end] == float("inf"):
            raise ParserError("no path between start and end")

        return self._rebuild_route(privious, end)

    def compute_k_route(self, start: str, end: str) -> list[list[Zone]]:
        routes = []
        used_connections = set()
        while True:
            original_connection = self.graph.connections
            self.graph.connections = [
                c for c in self.graph.connections
                if (min(c.zone1.name, c.zone2.name),
                    max(c.zone1.name, c.zone2.name)) not in used_connections
            ]
            try:
                route = self._compute_route(start, end)
            except Exception:
                break
            finally:
                self.graph.connections = original_connection
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
            raise ParserError("no route found!")
        return routes
