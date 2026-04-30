import re
from errors import ParserError
from zone import Zone
from graph import Graph


class Parser:
    DRONE_PATTERN = re.compile(r"^nb_drones:\s*([+-]?\d+)$")
    HUB_PATTERN = re.compile(
        r"^(?P<type>start_hub|end_hub|hub):\s+"
        r"(?P<name>\S+)\s+"
        r"(?P<x>[+-]?\d+)\s+"
        r"(?P<y>[+-]?\d+)"
        r"(?:\s+\[(?P<meta>[^\]]*)\])?$"
    )
    CONN_PATTERN = re.compile(
        r"^connection:\s+"
        r"(?P<name1>\S+)-(?P<name2>\S+)"
        r"(?:\s+\[(?P<meta>[^\]]*)\])?$"
    )

    def __init__(self) -> None:
        self.nb_drones: int = 0
        self.start_zone: Zone | None = None
        self.end_zone: Zone | None = None
        self.graph: Graph = Graph()

    def _clean_line(self, line: str) -> str:
        """Remove inline comments and strip whitespace."""
        if "#" in line:
            line = line[:line.index("#")]
        return line.strip()

    def _parse_hub_metadata(self, meta: str,
                            line_number: int) -> dict:
        """Parse metadata string from hub definition."""
        result: dict = {
            "zone_type": "normal",
            "color": None,
            "max_drones": 1
        }
        if not meta or not meta.strip():
            return result

        valid_keys = ["zone", "color", "max_drones"]
        valid_zone_types = ["normal", "blocked", "restricted", "priority"]
        pair_pattern = re.compile(r"^(\w+)=(\S+)$")

        for item in meta.strip().split():
            match = pair_pattern.match(item)
            if not match:
                raise ParserError(
                    f"Line {line_number}: invalid metadata '{item}'"
                )
            key, value = match.group(1), match.group(2)

            if key not in valid_keys:
                raise ParserError(
                    f"Line {line_number}: unknown metadata key '{key}' "
                    f"expected one of {valid_keys}"
                )
            if key == "zone":
                if value not in valid_zone_types:
                    raise ParserError(
                        f"Line {line_number}: invalid zone type '{value}' "
                        f"expected one of {valid_zone_types}"
                    )
                result["zone_type"] = value
            elif key == "color":
                if not value.isalpha():
                    raise ParserError(
                        f"Line {line_number}: color must be "
                        f"a single word got '{value}'"
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
                        "max_drones must be positive!"
                    )
        return result

    def _parse_conn_metadata(self, meta: str,
                             line_number: int) -> int:
        """Parse metadata string from connection definition."""
        if not meta or not meta.strip():
            return 1

        max_link_capacity = 1
        pair_pattern = re.compile(r"^(\w+)=(\S+)$")

        for item in meta.strip().split():
            match = pair_pattern.match(item)
            if not match:
                raise ParserError(
                    f"Line {line_number}: "
                    f"invalid connection metadata '{item}'"
                )
            key, value = match.group(1), match.group(2)

            if key != "max_link_capacity":
                raise ParserError(
                    f"Line {line_number}: "
                    f"unknown connection metadata '{key}' "
                    "expected 'max_link_capacity'"
                )
            try:
                max_link_capacity = int(value)
            except ValueError:
                raise ParserError(
                    f"Line {line_number}: "
                    "max_link_capacity must be integer!"
                )
            if max_link_capacity < 1:
                raise ParserError(
                    f"Line {line_number}: "
                    "max_link_capacity must be positive!"
                )
        return max_link_capacity

    def _handle_hub(self, match: re.Match,
                    line_number: int) -> None:
        """Handle start_hub, end_hub and hub lines."""
        hub_type = match.group("type")
        name = match.group("name")
        meta = match.group("meta")

        try:
            x = int(match.group("x"))
            y = int(match.group("y"))
        except ValueError:
            raise ParserError(
                f"Line {line_number}: coordinates must be integers!"
            )

        metadata = self._parse_hub_metadata(meta or "", line_number)

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

    def _handle_connection(self, match: re.Match,
                           line_number: int) -> None:
        """Handle connection lines."""
        name1 = match.group("name1")
        name2 = match.group("name2")
        meta = match.group("meta")

        if name1 == name2:
            raise ParserError(
                f"Line {line_number}: "
                "connection cannot link zone to itself!"
            )

        max_link_capacity = self._parse_conn_metadata(
            meta or "", line_number
        )
        self.graph.add_connection(name1, name2, max_link_capacity)

    def parse(self, filename: str) -> None:
        """Parse map file and build graph."""
        try:
            with open(filename, "r") as f:
                lines = f.readlines()
        except FileNotFoundError:
            raise ParserError(f"File '{filename}' not found!")

        if not lines:
            raise ParserError("Empty map file!")

        for line_number, line in enumerate(lines, 1):
            line = self._clean_line(line)

            if not line:
                continue

            # nb_drones must be first
            if self.nb_drones == 0:
                match = self.DRONE_PATTERN.match(line)
                if not match:
                    raise ParserError(
                        f"Line {line_number}: "
                        "first valid line must define 'nb_drones: <int>'"
                    )
                value = int(match.group(1))
                if value < 1:
                    raise ParserError(
                        f"Line {line_number}: "
                        "nb_drones must be at least 1!"
                    )
                self.nb_drones = value
                continue

            # nb_drones again?
            if self.DRONE_PATTERN.match(line):
                raise ParserError(
                    f"Line {line_number}: nb_drones already defined!"
                )

            # hub lines
            hub_match = self.HUB_PATTERN.match(line)
            if hub_match:
                self._handle_hub(hub_match, line_number)
                continue

            # connection lines
            conn_match = self.CONN_PATTERN.match(line)
            if conn_match:
                self._handle_connection(conn_match, line_number)
                continue

            raise ParserError(
                f"Line {line_number}: invalid syntax '{line}'"
            )

        # final validations
        if self.start_zone is None:
            raise ParserError("No start_hub defined!")
        if self.end_zone is None:
            raise ParserError("No end_hub defined!")
