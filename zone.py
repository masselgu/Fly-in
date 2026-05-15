from errors import ZoneError


class Zone:
    """Represents a zone in the graph with coordinates, type, color,
    and drone capacity."""
    def __init__(self, name: str, x: int, y: int,
                 zone_type: str = "normal",
                 color: str | None = None,
                 max_drones: int = 1) -> None:
        """Initialize a Zone with name, coordinates, type, optional color,
        and max drone capacity."""

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
