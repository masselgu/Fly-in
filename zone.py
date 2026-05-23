from errors import ZoneError


class Zone:
    """Represents a zone in the graph with coordinates, type, color,
    and drone capacity."""
    def __init__(self, name: str, x: int, y: int,
                 zone_type: str = "normal",
                 color: str | None = None,
                 max_drones: int = 1) -> None:
        """Initialize a Zone.

        Args:
            name: Unique zone identifier, no dashes or spaces allowed.
            x: X coordinate of the zone.
            y: Y coordinate of the zone.
            zone_type: One of 'normal', 'blocked', 'restricted', 'priority'.
            color: Optional display color name.
            max_drones: Maximum number of drones allowed simultaneously.

        Raises:
            ZoneError: If any argument is invalid.
        """

        if not name or '-' in name or ' ' in name:
            raise ZoneError(f"Invalid zone name: '{name}'")
        self.name = name

        if not isinstance(x, int) or not isinstance(y, int):
            raise ZoneError(f"Invalid coordinates: ({x}, {y})")
        self.x = x
        self.y = y

        valid_types = ["normal", "blocked", "restricted", "priority"]
        if zone_type not in valid_types:
            raise ZoneError(f"Invalid zone type: '{zone_type}'")
        self.zone_type = zone_type

        if color is not None and ' ' in color:
            raise ZoneError(f"Invalid color: '{color}'")
        self.color = color

        if not isinstance(max_drones, int) or max_drones < 1:
            raise ZoneError(f"Invalid max_drones: {max_drones}")
        self.max_drones = max_drones
