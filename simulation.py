import math
from drone import Drone
from graph import Graph
from zone import Zone
from pathfinder import Pathfinder
from flight_planner import FlightPlanner
from errors import SimulationError


class Simulation:
    """Drone fleet simulation engine."""

    def __init__(self, graph: Graph, pathfinder: Pathfinder,
                 start_zone: Zone, end_zone: Zone,
                 nb_drones: int) -> None:
        """Initialize and pre-book all drone routes."""
        self.graph = graph
        self.end_zone = end_zone
        self.planner = FlightPlanner()
        self.turn_log: list[str] = []
        self.drones: list[Drone] = []

        for i in range(1, nb_drones + 1):
            route = pathfinder.compute_route(
                start_zone.name, end_zone.name
            )
            self._prebook(route)
            self.drones.append(Drone(i, start_zone, route))

    def _prebook(self, route: list[Zone]) -> None:
        """Pre-book zone and link slots for a route."""
        turn: float = 0.0
        for i in range(len(route) - 1):
            cur, nxt = route[i], route[i + 1]
            w = 2.0 if nxt.zone_type == "restricted" else \
                0.9 if nxt.zone_type == "priority" else 1.0
            arrival = math.ceil(turn + w)
            while not self.planner.zone_is_free(
                    nxt.name, nxt.max_drones, arrival):
                arrival += 1
            cap = self._link_cap(cur.name, nxt.name)
            while not self.planner.link_is_free(
                    cur.name, nxt.name, cap, arrival):
                arrival += 1
            self.planner.book_zone(nxt.name, arrival)
            self.planner.book_link(cur.name, nxt.name, arrival)
            turn = arrival

    def _link_cap(self, a: str, b: str) -> int:
        """Return link capacity between two zones."""
        for c in self.graph.connections:
            if (c.zone1.name == a and c.zone2.name == b) or \
               (c.zone2.name == a and c.zone1.name == b):
                return c.max_link_capacity
        return 1

    def _occupancy(self) -> dict[str, list[Drone]]:
        """Return current zone occupancy."""
        occ: dict[str, list[Drone]] = {n: [] for n in self.graph.zones}
        for d in self.drones:
            if not d.is_done():
                occ[d.current_zone.name].append(d)
        return occ

    def _link_usage(self) -> dict[str, int]:
        """Return current link usage."""
        usage: dict[str, int] = {}
        for d in self.drones:
            if d.airborne and d.transit_label():
                label = d.transit_label()
                usage[label] = usage.get(label, 0) + 1  # type: ignore
        return usage

    def run(self) -> list[str]:
        """Run simulation until all drones reach destination."""
        turn = 0
        while not all(d.is_done() for d in self.drones):
            turn += 1
            occ = self._occupancy()
            usage = self._link_usage()
            moves: list[str] = []

            for d in sorted(self.drones,
                            key=lambda x: (-x.position, x.drone_id)):
                if d.is_done():
                    continue
                nxt = d.next_zone()
                if nxt is None:
                    continue

                if d.airborne:
                    if len(occ.get(nxt.name, [])) < nxt.max_drones:
                        occ[d.current_zone.name].remove(d)
                        d.fly()
                        occ[d.current_zone.name].append(d)
                        moves.append(
                            f"D{d.drone_id}-{d.current_zone.name}"
                        )
                    continue

                cap = self._link_cap(d.current_zone.name, nxt.name)
                lbl = f"{d.current_zone.name}-{nxt.name}"
                rev = f"{nxt.name}-{d.current_zone.name}"

                if len(occ.get(nxt.name, [])) >= nxt.max_drones:
                    continue
                if usage.get(lbl, 0) + usage.get(rev, 0) >= cap:
                    continue

                occ[d.current_zone.name].remove(d)
                if nxt.zone_type == "restricted":
                    usage[lbl] = usage.get(lbl, 0) + 1
                    d.fly()
                    moves.append(f"D{d.drone_id}-{d.transit_label()}")
                else:
                    d.fly()
                    occ[d.current_zone.name].append(d)
                    moves.append(
                        f"D{d.drone_id}-{d.current_zone.name}"
                    )

            if moves:
                self.turn_log.append(" ".join(moves))
            for d in self.drones:
                d.new_turn()

            if turn > 1000:
                raise SimulationError(
                    "fleet stuck after 1000 turns!"
                )

        return self.turn_log