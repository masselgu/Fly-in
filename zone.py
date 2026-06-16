from errors import ZoneError


class Zone:
    """Represent a zone in the graph."""

    def __init__(self, name: str, x: int, y: int,
                 zone_type: str = "normal",
                 color: str | None = None,
                 max_drones: int = 1) -> None:
        """Initialize a zone.

        Args:
            name: String zone identifier, without dashes or spaces.
            x: Integer x coordinate of the zone.
            y: Integer y coordinate of the zone.
            zone_type: String zone type, such as normal or restricted.
            color: Optional string display color name.
            max_drones: Integer maximum number of drones allowed at once.

        Returns:
            None.

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
