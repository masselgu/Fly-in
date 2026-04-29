from errors import ParserError
from zone import Zone
from graph import Graph


class Parser:
    def __init__(self) -> None:
        self.nb_drones: int = 0
        self.start_zone: Zone | None = None
        self.end_zone: Zone | None = None
        self.graph: Graph = Graph()

    def parse_metadata(self, metadata: str, line_number: int) -> dict:
        result: dict = {
            "zone_type": "normal",
            "color": None,
            "max_drones": 1
        }
        if not metadata.strip():
            return result
        for item in metadata.strip().split():
            if "=" not in item:
                raise ParserError(
                    f"Line {line_number}: invalid metadata '{item}'"
                )
            key, value = item.split("=", 1)
            if not key or not value or value.startswith("="):
                raise ParserError(
                    f"Line {line_number}: invalid metadata '{item}'"
                )
            if key == "zone":
                result["zone_type"] = value
            elif key == "color":
                result["color"] = value
            elif key == "max_drones":
                try:
                    result["max_drones"] = int(value)
                except ValueError:
                    raise ParserError(
                        f"Line {line_number}: max_drones must be integer!"
                    )
            else:
                raise ParserError(
                    f"Line {line_number}: unknown metadata key '{key}'"
                )
        return result

    def parse_hubs(self, line: str, line_number: int) -> Zone:
        line = line.strip()
        if not line:
            raise ParserError(
                f"Line {line_number}: hub value missing!"
            )
        if "[" in line:
            main_part, metadata_part = line.split("[", 1)
            if "]" not in metadata_part:
                raise ParserError(
                    f"Line {line_number}: missing closing ']'"
                )
            metadata_part = metadata_part.rstrip("]")
        else:
            main_part = line
            metadata_part = ""

        parts = main_part.strip().split()
        if len(parts) < 3:
            raise ParserError(
                f"Line {line_number}: hub must have name x y!"
            )
        if len(parts) > 3:
            raise ParserError(
                f"Line {line_number}: too many values before metadata!"
            )
        name = parts[0]
        try:
            x = int(parts[1])
            y = int(parts[2])
        except ValueError:
            raise ParserError(
                f"Line {line_number}: coordinates must be integers!"
            )
        metadata = self.parse_metadata(metadata_part, line_number)
        return Zone(
            name=name,
            x=x,
            y=y,
            zone_type=metadata["zone_type"],
            color=metadata["color"],
            max_drones=metadata["max_drones"]
        )

    def parse_connection(self, line: str, line_number: int) -> None:
        line = line.strip()
        if not line:
            raise ParserError(
                f"Line {line_number}: connection value missing!"
            )
        if "[" in line:
            main_part, metadata_part = line.split("[", 1)
            if "]" not in metadata_part:
                raise ParserError(
                    f"Line {line_number}: missing closing ']'"
                )
            metadata_part = metadata_part.rstrip("]")
        else:
            main_part = line
            metadata_part = ""

        main_part = main_part.strip()
        if "-" not in main_part:
            raise ParserError(
                f"Line {line_number}: connection must use '-' between zones!"
            )
        zone_names = main_part.split("-")
        if len(zone_names) != 2:
            raise ParserError(
                f"Line {line_number}: connection must have exactly 2 zones!"
            )
        name1 = zone_names[0].strip()
        name2 = zone_names[1].strip()

        if not name1 or not name2:
            raise ParserError(
                f"Line {line_number}: connection zone names missing!"
            )
        if name1 == name2:
            raise ParserError(
                f"Line {line_number}: connection cannot link zone to itself!"
            )

        max_link_capacity = 1
        if metadata_part.strip():
            for item in metadata_part.strip().split():
                if "=" not in item:
                    raise ParserError(
                        f"Line {line_number}: invalid metadata '{item}'"
                    )
                key, value = item.split("=", 1)
                if not key or not value or value.startswith("="):
                    raise ParserError(
                        f"Line {line_number}: invalid metadata '{item}'"
                    )
                if key == "max_link_capacity":
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
                else:
                    raise ParserError(
                        f"Line {line_number}: "
                        f"unknown connection metadata '{key}'"
                    )
        self.graph.add_connection(name1, name2, max_link_capacity)

    def parse(self, filename: str) -> None:
        try:
            with open(filename, "r") as f:
                for line_number, line in enumerate(f, 1):
                    line = line.strip()

                    if "#" in line:
                        line = line.split("#")[0].strip()

                    if not line:
                        continue

                    parts = line.split(":", 1)
                    if parts[0] not in ["nb_drones", "start_hub",
                                        "end_hub", "hub", "connection"]:
                        raise ParserError(
                            f"Line {line_number}: invalid input '{line}'"
                        )
                    if parts[0] != "nb_drones" and self.nb_drones == 0:
                        raise ParserError(
                            f"Line {line_number}: nb_drones must be first!"
                        )
                    if parts[0] == "nb_drones":
                        if self.nb_drones != 0:
                            raise ParserError(
                                f"Line {line_number}: "
                                "nb_drones already defined!"
                            )
                        if not parts[1].strip():
                            raise ParserError(
                                f"Line {line_number}: "
                                "nb_drones value missing!"
                            )
                        try:
                            self.nb_drones = int(parts[1].strip())
                        except ValueError:
                            raise ParserError(
                                f"Line {line_number}: "
                                "nb_drones must be integer!"
                            )
                        if self.nb_drones < 1:
                            raise ParserError(
                                f"Line {line_number}: "
                                "nb_drones must be positive!"
                            )
                    elif parts[0] == "start_hub":
                        if self.start_zone is not None:
                            raise ParserError(
                                f"Line {line_number}: "
                                "start_hub already defined!"
                            )
                        self.start_zone = self.parse_hubs(
                            parts[1], line_number
                        )
                        self.graph.add_zone(self.start_zone)
                    elif parts[0] == "end_hub":
                        if self.end_zone is not None:
                            raise ParserError(
                                f"Line {line_number}: "
                                "end_hub already defined!"
                            )
                        self.end_zone = self.parse_hubs(
                            parts[1], line_number
                        )
                        self.graph.add_zone(self.end_zone)
                    elif parts[0] == "hub":
                        self.graph.add_zone(
                            self.parse_hubs(parts[1], line_number)
                        )
                    elif parts[0] == "connection":
                        self.parse_connection(parts[1], line_number)

            if self.start_zone is None:
                raise ParserError("No start_hub defined!")
            if self.end_zone is None:
                raise ParserError("No end_hub defined!")

        except FileNotFoundError:
            raise ParserError(f"File '{filename}' not found!")
