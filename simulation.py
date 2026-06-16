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
        """Initialize the simulation.

        Args:
            graph: Graph object to simulate on.
            paths: List of routes, where each route is a list of zone names.
            nb_drones: Integer total number of drones to simulate.
            end_zone: Destination zone name as a string.

        Returns:
            None.
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
            a: First zone name as a string.
            b: Second zone name as a string.

        Returns:
            Tuple of the two zone names sorted alphabetically.
        """
        return (min(a, b), max(a, b))

    def _conn_name(self, a: str, b: str) -> str:
        """Return the human-readable connection label for output.

        Args:
            a: Source zone name as a string.
            b: Destination zone name as a string.

        Returns:
            String connection name in the format "a-b".
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
        """Check whether a drone can move this turn.

        Args:
            drone: Drone object attempting to move.
            next_zone: Target zone name as a string.
            leaving: Dictionary of drones leaving each zone this turn.
            entering: Dictionary of drones entering each zone this turn.
            conn_used: Dictionary of connection usage counts this turn.

        Returns:
            Boolean indicating whether the move is valid.
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
            List of strings, one per turn, describing drone movements.
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
                    executed.append((drone, next_zone))
                    edge = self._conn_key(drone.current_zone, next_zone)
                    conn_used[edge] = conn_used.get(edge, 0) + 1
                else:
                    if self.can_move(
                        drone, next_zone, leaving, entering, conn_used
                    ):
                        executed.append((drone, next_zone))
                        edge = self._conn_key(drone.current_zone, next_zone)
                        conn_used[edge] = conn_used.get(edge, 0) + 1

                if (drone, next_zone) in executed:
                    leaving[drone.current_zone] = (
                        leaving.get(drone.current_zone, 0) + 1
                    )
                    entering[next_zone] = entering.get(next_zone, 0) + 1

            for drone, next_zone in executed:
                zone = self.graph.zones[next_zone]
                old_zone = drone.current_zone

                if drone.in_transit:
                    self.zone_usage[next_zone] += 1
                    drone.complete_transit()
                    turn_moves.append(f"D{drone.drone_id}-{next_zone}")

                elif zone.zone_type == "restricted":
                    self.zone_usage[old_zone] -= 1
                    conn_label = self._conn_name(old_zone, next_zone)
                    drone.start_transit(next_zone)
                    turn_moves.append(f"D{drone.drone_id}-{conn_label}")

                else:
                    self.zone_usage[old_zone] -= 1
                    self.zone_usage[next_zone] += 1
                    drone.move_forward()
                    turn_moves.append(f"D{drone.drone_id}-{next_zone}")

            if turn_moves:
                self.logs.append(" ".join(turn_moves))
        return self.logs
