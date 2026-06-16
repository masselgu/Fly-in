class Drone:
    """Represent one drone moving through a planned route."""

    def __init__(
        self,
        drone_id: int,
        start_zone: str,
        path: list[str],
    ) -> None:
        """Initialize a drone.

        Args:
            drone_id: Integer identifier used in output.
            start_zone: Starting zone name as a string.
            path: Ordered list of zone names from start to destination.

        Returns:
            None.
        """
        self.drone_id = drone_id
        self.current_zone = start_zone
        self.path = path
        self.path_index = 0
        self.finished = False
        self.in_transit = False
        self.transit_target = ""

    def next_zone(self) -> str | None:
        """Return the next zone in the path.

        Returns:
            String name of the next zone, or None if the route is complete.
        """
        if self.path_index + 1 < len(self.path):
            return self.path[self.path_index + 1]
        return None

    def move_forward(self) -> None:
        """Advance the drone one step along its path.

        Returns:
            None.
        """
        self.path_index += 1
        self.current_zone = self.path[self.path_index]
        if self.path_index == len(self.path) - 1:
            self.finished = True

    def start_transit(self, target_zone: str) -> None:
        """Begin a two-turn transit toward a restricted zone.

        Args:
            target_zone: Restricted zone name as a string.

        Returns:
            None.
        """
        self.in_transit = True
        self.transit_target = target_zone
        self.path_index += 1

    def complete_transit(self) -> None:
        """Finish transit and land in the target zone.

        Returns:
            None.
        """
        self.in_transit = False
        self.current_zone = self.transit_target
        self.transit_target = ""
        if self.path_index == len(self.path) - 1:
            self.finished = True
