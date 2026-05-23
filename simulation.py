from graph import Graph, Connection
from drone import Drone
from typing import List, Dict


class Simulation:
    """Run the drone routing simulation turn by turn."""
    def __init__(
        self,
        graph: Graph,
        paths: List[List[str]],
        nb_drones: int,
        end_zone: str
    ) -> None:
        """Initialize the simulation with the graph, drone paths, and end zone.

        Args:
            graph: The zone graph to simulate on.
            paths: List of paths (each a list of zone names) to assign to
            drones.
            nb_drones: Total number of drones to simulate.
            end_zone: Name of the destination zone.
        """
        self.graph = graph
        self.end_zone = end_zone

        self.drones: List[Drone] = []
        for i in range(1, nb_drones + 1):
            path = paths[(i - 1) % len(paths)]
            self.drones.append(Drone(i, path[0], path))

        self.logs: List[str] = []

        start_name = self.drones[0].path[0]
        self.zone_usage: Dict[str, int] = {z: 0 for z in self.graph.zones}
        self.zone_usage[start_name] = nb_drones

        self.connection_map: Dict[tuple[str, str], Connection] = {}
        for conn in self.graph.connections:
            key = (
                min(conn.zone1.name, conn.zone2.name),
                max(conn.zone1.name, conn.zone2.name)
            )
            self.connection_map[key] = conn

    def _conn_key(self, a: str, b: str) -> tuple[str, str]:
        """Return a canonical sorted key for a connection.

        Args:
            a: First zone name.
            b: Second zone name.

        Returns:
            A tuple (min, max) of the two zone names.
        """
        return (min(a, b), max(a, b))

    def _conn_name(self, a: str, b: str) -> str:
        """Return the human-readable connection label for output.

        Args:
            a: Source zone name.
            b: Destination zone name.

        Returns:
            A string in the format 'a-b'.
        """
        return f"{a}-{b}"

    def can_move(
        self,
        drone: Drone,
        next_zone: str,
        leaving: Dict[str, int],
        entering: Dict[str, int],
        conn_used: Dict[tuple[str, str], int],
    ) -> bool:
        """Check if a drone can move to next_zone this turn.

        Args:
            drone: The drone attempting to move.
            next_zone: Name of the target zone.
            leaving: Drones leaving each zone this turn.
            entering: Drones entering each zone this turn.
            conn_used: Connections already used this turn.

        Returns:
            True if the move is valid, False otherwise.
        """
        if next_zone not in self.graph.zones:
            return False

        zone = self.graph.zones[next_zone]

        if zone.zone_type == "blocked":
            return False

        if next_zone != self.end_zone:
            current = self.zone_usage.get(next_zone, 0)
            effective = (
                current
                - leaving.get(next_zone, 0)
                + entering.get(next_zone, 0)
            )
            if effective >= zone.max_drones:
                return False

        edge = self._conn_key(drone.current_zone, next_zone)
        conn = self.connection_map.get(edge)
        if conn is None:
            return False

        if conn_used.get(edge, 0) >= conn.max_link_capacity:
            return False

        return True

    def run(self) -> List[str]:
        """Run the simulation and return the turn-by-turn log.

        Returns:
            A list of strings, one per turn, describing all drone movements.
        """
        while not all(d.finished for d in self.drones):
            leaving: Dict[str, int] = {}
            entering: Dict[str, int] = {}
            conn_used: Dict[tuple[str, str], int] = {}
            turn_moves: List[str] = []

            candidates: List[tuple[Drone, str]] = []
            for drone in sorted(self.drones, key=lambda d: d.drone_id):
                if drone.finished:
                    continue

                if drone.in_transit:
                    candidates.append((drone, drone.transit_target))
                    continue

                nxt = drone.next_zone()
                if nxt is not None:
                    candidates.append((drone, nxt))

            executed: List[tuple[Drone, str]] = []

            for drone, next_zone in candidates:
                zone = self.graph.zones[next_zone]

                if drone.in_transit:
                    current = self.zone_usage.get(next_zone, 0)
                    effective = (
                        current
                        - leaving.get(next_zone, 0)
                        + entering.get(next_zone, 0)
                    )
                    if effective < zone.max_drones or \
                       next_zone == self.end_zone:
                        executed.append((drone, next_zone))
                else:
                    if self.can_move(
                        drone, next_zone, leaving, entering, conn_used
                    ):
                        executed.append((drone, next_zone))

                if (drone, next_zone) in executed:
                    leaving[drone.current_zone] = (
                        leaving.get(drone.current_zone, 0) + 1
                    )
                    entering[next_zone] = entering.get(next_zone, 0) + 1
                    edge = self._conn_key(drone.current_zone, next_zone)
                    conn_used[edge] = conn_used.get(edge, 0) + 1

            for drone, next_zone in executed:
                zone = self.graph.zones[next_zone]
                old_zone = drone.current_zone

                self.zone_usage[old_zone] -= 1
                self.zone_usage[next_zone] += 1

                if drone.in_transit:
                    drone.complete_transit()
                    turn_moves.append(f"D{drone.drone_id}-{next_zone}")
                elif zone.zone_type == "restricted":
                    conn_label = self._conn_name(old_zone, next_zone)
                    drone.start_transit(next_zone)
                    self.zone_usage[next_zone] -= 1
                    turn_moves.append(f"D{drone.drone_id}-{conn_label}")
                else:
                    drone.move_forward()
                    turn_moves.append(f"D{drone.drone_id}-{next_zone}")

            if turn_moves:
                self.logs.append(" ".join(turn_moves))

        return self.logs
