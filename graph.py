from errors import GraphError
from zone import Zone


class Connection:
    """Represent a bidirectional connection between two zones."""

    def __init__(self, zone1: Zone, zone2: Zone,
                 max_link_capacity: int = 1) -> None:
        """Initialize a connection.

        Args:
            zone1: First Zone object connected by the edge.
            zone2: Second Zone object connected by the edge.
            max_link_capacity: Integer maximum simultaneous drone crossings.

        Returns:
            None.

        Raises:
            GraphError: If max_link_capacity is not a positive integer.
        """
        if not isinstance(max_link_capacity, int) or max_link_capacity < 1:
            raise GraphError(f"Invalid capacity: {max_link_capacity}")
        self.zone1 = zone1
        self.zone2 = zone2
        self.max_link_capacity = max_link_capacity


class Graph:
    """Represent the zone graph and its connections."""

    def __init__(self) -> None:
        """Initialize an empty graph.

        Returns:
            None.
        """
        self.zones: dict[str, Zone] = {}
        self.connections: list[Connection] = []

    def add_zone(self, zone: Zone) -> None:
        """Add a zone to the graph.

        Args:
            zone: Zone object to store by name.

        Returns:
            None.

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
            name1: String name of the first zone.
            name2: String name of the second zone.
            max_link_capacity: Integer maximum simultaneous drone crossings.

        Returns:
            None.

        Raises:
            GraphError: If a zone is missing or the connection already exists.
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
            name: String name of the zone to inspect.

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
