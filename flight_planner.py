class FlightPlanner:
    """Pre-books zone and link slots for future simulation turns."""

    def __init__(self) -> None:
        """Initialize empty booking tables."""
        self.zone_bookings: dict[str, dict[int, int]] = {}
        self.link_bookings: dict[tuple[str, str], dict[int, int]] = {}

    def zone_is_free(self, name: str,
                     capacity: int, turn: int) -> bool:
        """Check if zone has space at a given turn."""
        return self.zone_bookings.get(name, {}).get(turn, 0) < capacity

    def link_is_free(self, a: str, b: str,
                     capacity: int, turn: int) -> bool:
        """Check if link has space at a given turn."""
        key: tuple[str, str] = tuple(sorted([a, b]))  # type: ignore
        return self.link_bookings.get(key, {}).get(turn, 0) < capacity

    def book_zone(self, name: str, turn: int) -> None:
        """Reserve a slot in a zone for a given turn."""
        if name not in self.zone_bookings:
            self.zone_bookings[name] = {}
        self.zone_bookings[name][turn] = \
            self.zone_bookings[name].get(turn, 0) + 1

    def book_link(self, a: str, b: str, turn: int) -> None:
        """Reserve a link slot between two zones for a given turn."""
        key: tuple[str, str] = tuple(sorted([a, b]))  # type: ignore
        if key not in self.link_bookings:
            self.link_bookings[key] = {}
        self.link_bookings[key][turn] = \
            self.link_bookings[key].get(turn, 0) + 1
