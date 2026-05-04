from zone import Zone


class Drone:
    """Drone unit navigator."""

    def __init__(self, drone_id: int,
                 start_zone: Zone,
                 path: list[Zone]) -> None:
        """Initialize drone with id, start zone and path."""
        self.drone_id: int = drone_id
        self.current_zone: Zone = start_zone
        self.path: list[Zone] = path[:]
        self.position: int = 0
        self.finished: bool = False
        self.turn_consumed: bool = False
        self.turns_until_landing: int = 0
        self.airborne: bool = False

    def next_zone(self) -> Zone | None:
        """Return next zone in path."""
        if self.position + 1 < len(self.path):
            return self.path[self.position + 1]
        return None

    def fly(self) -> None:
        """Advance drone one step along path."""
        if self.finished or self.turn_consumed:
            return
        upcoming = self.next_zone()
        if upcoming is None:
            self.finished = True
            return
        if not self.airborne:
            if upcoming.zone_type == "restricted":
                self.airborne = True
                self.turns_until_landing = 1
            else:
                self.position += 1
                self.current_zone = self.path[self.position]
        else:
            self.turns_until_landing -= 1
            if self.turns_until_landing <= 0:
                self.airborne = False
                self.position += 1
                self.current_zone = self.path[self.position]
        self.turn_consumed = True
        if self.position == len(self.path) - 1:
            self.finished = True

    def new_turn(self) -> None:
        """Reset turn flag."""
        self.turn_consumed = False

    def steps_remaining(self) -> int:
        """Return steps left to destination."""
        return len(self.path) - 1 - self.position

    def transit_label(self) -> str | None:
        """Return connection label when airborne."""
        if self.airborne and self.next_zone() is not None:
            return f"{self.current_zone.name}-{self.next_zone().name}"  # type: ignore
        return None

    def is_done(self) -> bool:
        """Return True if drone reached destination."""
        return self.finished

    def __str__(self) -> str:
        """Return drone identifier."""
        return f"D{self.drone_id}"
