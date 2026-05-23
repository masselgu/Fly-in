from errors import GraphError
from zone import Zone


class Connection:
    """Represents a bidirectional connection between two zones with a
    maximum capacity."""
    def __init__(self, zone1: Zone, zone2: Zone,
                 max_link_capacity: int = 1) -> None:
        """Initialize a connection between two zones.

        Args:
            zone1: First zone of the connection.
            zone2: Second zone of the connection.
            max_link_capacity: Max drones traversing simultaneously.

        Raises:
            GraphError: If max_link_capacity is not a positive integer.
        """
        if not isinstance(max_link_capacity, int) or max_link_capacity < 1:
            raise GraphError(f"Invalid capacity: {max_link_capacity}")
        self.zone1 = zone1
        self.zone2 = zone2
        self.max_link_capacity = max_link_capacity


class Graph:
    """Represents the entire zone graph, including zones and connections."""
    def __init__(self) -> None:
        """Initialize the graph with empty zone and connection lists."""
        self.zones: dict[str, Zone] = {}
        self.connections: list[Connection] = []

    def add_zone(self, zone: Zone) -> None:
        """Add a zone to the graph.

        Args:
            zone: The Zone object to add.

        Raises:
            GraphError: If a zone with the same name already exists.
        """
        if zone.name in self.zones:
            raise GraphError(f"Zone '{zone.name}' already exists!")
        self.zones[zone.name] = zone

    def add_connection(self, name1: str, name2: str,
                       max_link_capacity: int = 1) -> None:
        """Add a bidirectional connection between two zones.

        Args:
            name1: Name of the first zone.
            name2: Name of the second zone.
            max_link_capacity: Max drones allowed simultaneously.

        Raises:
            GraphError: If either zone is missing or connection exists.
        """
        if name1 not in self.zones:
            raise GraphError(f"Zone '{name1}' not found!")
        if name2 not in self.zones:
            raise GraphError(f"Zone '{name2}' not found!")

        for conn in self.connections:
            if (conn.zone1.name == name1 and conn.zone2.name == name2) or \
               (conn.zone1.name == name2 and conn.zone2.name == name1):
                raise GraphError(
                    f"Connection '{name1}-{name2}' already exists!"
                )

        zone1 = self.zones[name1]
        zone2 = self.zones[name2]
        self.connections.append(Connection(zone1, zone2, max_link_capacity))

    def get_neighbors(self, name: str) -> list[Zone]:
        """Return all zones directly connected to the given zone.

        Args:
            name: Name of the zone to look up.

        Returns:
            List of neighboring Zone objects.
        """
        neighbors = []
        for conn in self.connections:
            if conn.zone1.name == name:
                neighbors.append(conn.zone2)
            elif conn.zone2.name == name:
                neighbors.append(conn.zone1)
        return neighbors
