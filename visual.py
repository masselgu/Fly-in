from graph import Graph


COLORS: dict[str, str] = {
    "red":     "\033[31m",
    "green":   "\033[32m",
    "yellow":  "\033[33m",
    "blue":    "\033[34m",
    "magenta": "\033[35m",
    "cyan":    "\033[36m",
    "white":   "\033[37m",
    "gray":    "\033[90m",
    "reset":   "\033[0m",
}


class Visual:
    """Handles colored terminal output for simulation."""

    @staticmethod
    def colorize(text: str, color: str | None) -> str:
        """Wrap text with terminal color code."""
        if color and color in COLORS:
            return f"{COLORS[color]}{text}{COLORS['reset']}"
        return text

    @staticmethod
    def display(logs: list[str], graph: Graph,
                nb_drones: int) -> None:
        """Display full simulation output with colors."""
        print(Visual.colorize(
            f"Simulation started — {nb_drones} drones",
            "cyan"
        ))
        print(Visual.colorize(
            "─" * 40, "cyan"
        ))

        for i, log in enumerate(logs, 1):
            colored_log = Visual._colorize_log(log, graph)
            print(Visual.colorize(f"Turn {i}: ", "yellow") + colored_log)

        print(Visual.colorize("─" * 40, "cyan"))
        print(Visual.colorize(
            f"Simulation complete — {len(logs)} turns total!",
            "green"
        ))

        Visual._display_stats(logs, nb_drones)

    @staticmethod
    def _colorize_log(log: str, graph: Graph) -> str:
        """Colorize each drone movement in a log line."""
        colored_moves: list[str] = []
        for move in log.split():
            parts = move.split("-", 1)
            drone = parts[0]
            zone_name = parts[1] if len(parts) > 1 else ""

            # get zone color
            zone_color = None
            clean_name = zone_name.split("-")[0]
            if clean_name in graph.zones:
                zone_color = graph.zones[clean_name].color

            colored_zone = Visual.colorize(zone_name, zone_color)
            colored_moves.append(
                Visual.colorize(drone, "magenta") + "-" + colored_zone
            )
        return " ".join(colored_moves)

    @staticmethod
    def _display_stats(logs: list[str], nb_drones: int) -> None:
        """Display simulation statistics."""
        total_moves = sum(len(log.split()) for log in logs)
        avg = round(total_moves / nb_drones, 2) if nb_drones > 0 else 0

        print(Visual.colorize("\nStatistics:", "cyan"))
        print(f"  Total turns     : {Visual.colorize(str(len(logs)), 'yellow')}")
        print(f"  Total moves     : {Visual.colorize(str(total_moves), 'yellow')}")
        print(f"  Avg turns/drone : {Visual.colorize(str(avg), 'yellow')}")
