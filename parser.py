import matplotlib.colors as mcolors
from errors import ParserError
from zone import Zone
from graph import Graph


class Parser:
    """Parse map files into a graph structure."""

    def __init__(self) -> None:
        """Initialize empty parser state.

        Returns:
            None.
        """
        self.nb_drones: int = 0
        self.start_zone: Zone | None = None
        self.end_zone: Zone | None = None
        self.graph: Graph = Graph()

    def _clean_line(self, line: str) -> str:
        """Remove inline comments and strip whitespace.

        Args:
            line: Raw map file line as a string.

        Returns:
            Cleaned string without comments or surrounding whitespace.
        """
        if "#" in line:
            line = line[:line.index("#")]
        return line.strip()

    def _parse_metadata(self, data: str, line_number: int,
                        is_connection: bool = False) -> dict:
        """Parse metadata key-value pairs.

        Args:
            data: Bracket content string to parse.
            line_number: Integer source line number for error messages.
            is_connection: Boolean selecting connection metadata rules.

        Returns:
            Dictionary containing parsed metadata values.

        Raises:
            ParserError: If any metadata is invalid.
        """
        result: dict = {
            "zone_type": "normal",
            "color": None,
            "max_drones": 1,
            "max_link_capacity": 1
        }

        if not data.strip():
            return result

        valid_zone_keys = ["zone", "color", "max_drones"]
        valid_zone_types = ["normal", "blocked", "restricted", "priority"]

        for item in data.strip().split():
            if "=" not in item:
                raise ParserError(
                    f"Line {line_number}: invalid metadata '{item}'"
                )

            eq_index = item.index("=")
            key = item[:eq_index]
            value = item[eq_index + 1:]

            if not key.strip() or not value.strip():
                raise ParserError(
                    f"Line {line_number}: invalid metadata '{item}'"
                )

            if is_connection:
                if key != "max_link_capacity":
                    raise ParserError(
                        f"Line {line_number}: "
                        f"unknown connection metadata '{key}' "
                        "expected 'max_link_capacity'"
                    )
                try:
                    result["max_link_capacity"] = int(value)
                except ValueError:
                    raise ParserError(
                        f"Line {line_number}: "
                        "max_link_capacity must be integer!"
                    )
                if result["max_link_capacity"] < 1:
                    raise ParserError(
                        f"Line {line_number}: "
                        "max_link_capacity must be positive and non-zero! "
                    )
            else:
                if key not in valid_zone_keys:
                    raise ParserError(
                        f"Line {line_number}: unknown metadata key '{key}' "
                        f"expected one of {valid_zone_keys}"
                    )

                if key == "zone":
                    if value not in valid_zone_types:
                        raise ParserError(
                            f"Line {line_number}: invalid zone type '{value}' "
                            f"expected one of {valid_zone_types}"
                        )
                    result["zone_type"] = value

                elif key == "color":
                    if value.lower() != "rainbow" \
                     and value.lower() not in mcolors.CSS4_COLORS:
                        raise ParserError(
                            f"Line {line_number}: invalid color '{value}' "
                            "expected a valid color name"
                        )
                    result["color"] = value

                elif key == "max_drones":
                    try:
                        result["max_drones"] = int(value)
                    except ValueError:
                        raise ParserError(
                            f"Line {line_number}: "
                            "max_drones must be integer!"
                        )
                    if result["max_drones"] < 1:
                        raise ParserError(
                            f"Line {line_number}: "
                            "max_drones must be positive and non-zero!"
                        )

        return result

    def _extract_bracket_data(self, line: str,
                              line_number: int) -> tuple[str, str]:
        """Split a line into main content and bracket metadata.

        Args:
            line: Full cleaned map line as a string.
            line_number: Integer source line number for error messages.

        Returns:
            Tuple containing main content and bracket content strings.

        Raises:
            ParserError: If brackets are malformed.
        """
        if "[" in line:
            if "]" not in line:
                raise ParserError(
                    f"Line {line_number}: unclosed bracket"
                )
            bracket_start = line.index("[")
            bracket_end = line.index("]")
            main = line[:bracket_start].strip()
            data = line[bracket_start + 1:bracket_end].strip()
            after_bracket = line[bracket_end + 1:].strip()
            if after_bracket:
                raise ParserError(
                    f"Line {line_number}: unexpected content after "
                    "closing bracket"
                )
        else:
            main = line.strip()
            data = ""
        return main, data

    def _handle_nb_drones(self, line: str, line_number: int) -> None:
        """Parse and store the nb_drones value.

        Args:
            line: nb_drones line as a string.
            line_number: Integer source line number for error messages.

        Returns:
            None.

        Raises:
            ParserError: If value is missing, invalid, or less than 1.
        """
        parts = line.split(":")
        if len(parts) != 2:
            raise ParserError(
                f"Line {line_number}: "
                "first valid line must define 'nb_drones: <int>'"
            )
        value_str = parts[1].strip()
        if not value_str:
            raise ParserError(
                f"Line {line_number}: nb_drones value is missing!"
            )
        try:
            value = int(value_str)
        except ValueError:
            raise ParserError(
                f"Line {line_number}: nb_drones must be an integer!"
            )
        if value < 1:
            raise ParserError(
                f"Line {line_number}: nb_drones must be at least 1!"
            )
        self.nb_drones = value

    def _handle_hub(self, line: str, line_number: int) -> None:
        """Parse a hub line and add it to the graph.

        Args:
            line: Hub, start_hub, or end_hub line as a string.
            line_number: Integer source line number for error messages.

        Returns:
            None.

        Raises:
            ParserError: If syntax or metadata is invalid.
        """
        main, data = self._extract_bracket_data(line, line_number)

        colon_index = main.index(":")
        hub_type = main[:colon_index].strip()
        rest = main[colon_index + 1:].strip()

        parts = rest.split()
        if len(parts) != 3:
            raise ParserError(
                f"Line {line_number}: "
                "hub must have <name> <x> <y>"
            )

        name = parts[0]
        if not name or "-" in name or " " in name:
            raise ParserError(
                f"Line {line_number}: invalid zone name '{name}'"
            )
        if name in self.graph.zones:
            raise ParserError(
                f"Line {line_number}: zone '{name}' already exists!"
            )

        x_str = parts[1]
        y_str = parts[2]
        try:
            x = int(x_str)
            y = int(y_str)
        except ValueError:
            raise ParserError(
                f"Line {line_number}: coordinates must be integers!"
            )

        metadata = self._parse_metadata(data, line_number)

        zone = Zone(
            name=name,
            x=x,
            y=y,
            zone_type=metadata["zone_type"],
            color=metadata["color"],
            max_drones=metadata["max_drones"]
        )

        if hub_type == "start_hub":
            if self.start_zone is not None:
                raise ParserError(
                    f"Line {line_number}: start_hub already defined!"
                )
            self.start_zone = zone

        elif hub_type == "end_hub":
            if self.end_zone is not None:
                raise ParserError(
                    f"Line {line_number}: end_hub already defined!"
                )
            self.end_zone = zone

        self.graph.add_zone(zone)

    def _handle_connection(self, line: str, line_number: int) -> None:
        """Parse a connection line and add it to the graph.

        Args:
            line: Connection line as a string.
            line_number: Integer source line number for error messages.

        Returns:
            None.

        Raises:
            ParserError: If syntax or zones are invalid.
        """
        main, data = self._extract_bracket_data(line, line_number)

        colon_index = main.index(":")
        rest = main[colon_index + 1:].strip()

        if "-" not in rest:
            raise ParserError(
                f"Line {line_number}: "
                "connection must follow format zone1-zone2"
            )

        dash_index = rest.index("-")
        zone1 = rest[:dash_index]
        zone2 = rest[dash_index + 1:]

        if not zone1.strip() or not zone2.strip():
            raise ParserError(
                f"Line {line_number}: "
                "connection must have two zone names"
            )

        if zone1 == zone2:
            raise ParserError(
                f"Line {line_number}: "
                "connection cannot link zone to itself!"
            )

        if zone1 not in self.graph.zones:
            raise ParserError(
                f"Line {line_number}: zone '{zone1}' not found!"
            )
        if zone2 not in self.graph.zones:
            raise ParserError(
                f"Line {line_number}: zone '{zone2}' not found!"
            )

        for conn in self.graph.connections:
            if (conn.zone1.name == zone1 and conn.zone2.name == zone2) or \
               (conn.zone1.name == zone2 and conn.zone2.name == zone1):
                raise ParserError(
                    f"Line {line_number}: "
                    f"connection '{zone1}-{zone2}' already exists!"
                )

        metadata = self._parse_metadata(data, line_number,
                                        is_connection=True)
        self.graph.add_connection(zone1, zone2,
                                  metadata["max_link_capacity"])

    def parse(self, filename: str) -> None:
        """Parse a map file and build the zone graph.

        Args:
            filename: String path to the map file.

        Returns:
            None.

        Raises:
            ParserError: If the file is missing, empty, or contains errors.
        """
        try:
            with open(filename, "r") as f:
                lines = f.readlines()
        except FileNotFoundError:
            raise ParserError(f"File '{filename}' not found!")
        except PermissionError:
            raise ParserError(f"Permission denied for file '{filename}'!")

        if not lines:
            raise ParserError("Empty map file!")

        for line_number, line in enumerate(lines, 1):
            line = self._clean_line(line)

            if not line:
                continue

            if self.nb_drones == 0:
                if not line.startswith("nb_drones:"):
                    raise ParserError(
                        f"Line {line_number}: "
                        "first valid line must define 'nb_drones: <int>'"
                    )
                self._handle_nb_drones(line, line_number)
                continue

            if line.startswith("nb_drones:"):
                raise ParserError(
                    f"Line {line_number}: nb_drones already defined!"
                )

            if (line.startswith("hub:") or
                    line.startswith("start_hub:") or
                    line.startswith("end_hub:")):
                self._handle_hub(line, line_number)
                continue

            if line.startswith("connection:"):
                self._handle_connection(line, line_number)
                continue

            raise ParserError(
                f"Line {line_number}: invalid syntax '{line}'"
            )

        if self.start_zone is None:
            raise ParserError("No start_hub defined!")
        if self.start_zone.zone_type == "blocked":
            raise ParserError("start_hub cannot be blocked!")
        if self.end_zone is None:
            raise ParserError("No end_hub defined!")
        if self.end_zone.zone_type == "blocked":
            raise ParserError("end_hub cannot be blocked!")

        coords: set[tuple[int, int]] = set()
        for zone in self.graph.zones.values():
            coord = (zone.x, zone.y)
            if coord in coords:
                raise ParserError(
                    f"Duplicate coordinates ({zone.x}, {zone.y}) "
                    f"for zone '{zone.name}'!"
                )
            coords.add(coord)

        if not self.graph.connections:
            raise ParserError("Map must have at least one connection!")
