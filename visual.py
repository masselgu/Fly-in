import matplotlib.colors as mcolors
from graph import Graph


class Visualizer:
    """Handle colored terminal output for the simulation."""

    RESET = "\033[0m"

    RAINBOW_COLORS = [
        mcolors.to_rgb("red"),
        mcolors.to_rgb("orange"),
        mcolors.to_rgb("yellow"),
        mcolors.to_rgb("green"),
        mcolors.to_rgb("blue"),
        mcolors.to_rgb("indigo"),
        mcolors.to_rgb("violet"),
    ]

    def __init__(self, graph: Graph) -> None:
        """Initialize the visualizer.

        Args:
            graph: Graph object used to find zone colors.

        Returns:
            None.
        """
        self.graph = graph

    def get_ansi(self, color_name: str) -> str:
        """Convert a color name to an ANSI escape code.

        Args:
            color_name: String color name accepted by matplotlib.

        Returns:
            ANSI escape code string for the color, or white if invalid.
        """
        try:
            r, g, b = (int(c * 255) for c in mcolors.to_rgb(color_name))
            return f"\033[38;2;{r};{g};{b}m"
        except ValueError:
            return "\033[97m"

    def apply_color(self, text: str, color_name: str) -> str:
        """Apply color formatting to text.

        Args:
            text: String text to color.
            color_name: String color name or rainbow.

        Returns:
            String wrapped with ANSI color escape codes.
        """
        if color_name.lower() == "rainbow":
            result = ""

            for i, char in enumerate(text):
                rgb = self.RAINBOW_COLORS[
                    i % len(self.RAINBOW_COLORS)
                ]
                r, g, b = (int(c * 255) for c in rgb)

                result += (
                    f"\033[38;2;{r};{g};{b}m"
                    f"{char}"
                    f"{self.RESET}"
                )

            return result

        return (
            f"{self.get_ansi(color_name)}"
            f"{text}"
            f"{self.RESET}"
        )

    def zone_color_name(self, zone_name: str) -> str:
        """Return a zone's color name.

        Args:
            zone_name: String name of the zone to inspect.

        Returns:
            String color name, or an empty string when no color is set.
        """
        zone = self.graph.zones.get(zone_name)

        if zone and zone.color:
            return zone.color

        return ""

    def print_turn(self, moves: str) -> None:
        """Print one simulation turn.

        Args:
            moves: String containing all move tokens for one turn.

        Returns:
            None.
        """
        for token in moves.split():
            dash = token.index("-")
            drone_id = token[:dash]
            rest = token[dash + 1:]

            last_dash = rest.rfind("-")

            if (
                last_dash != -1
                and rest[last_dash + 1:] in self.graph.zones
                and rest[:last_dash] in self.graph.zones
            ):
                zone1 = rest[:last_dash]
                zone2 = rest[last_dash + 1:]

                c1 = self.zone_color_name(zone1)
                c2 = self.zone_color_name(zone2)

                colored1 = (
                    self.apply_color(zone1, c1)
                    if c1 else zone1
                )
                colored2 = (
                    self.apply_color(zone2, c2)
                    if c2 else zone2
                )

                print(
                    f"{drone_id}-{colored1}-{colored2}",
                    end=" "
                )

            else:
                color = self.zone_color_name(rest)

                colored = (
                    self.apply_color(rest, color)
                    if color else rest
                )

                print(
                    f"{drone_id}-{colored}",
                    end=" "
                )

        print()

    def print_summary(
        self,
        total_turns: int,
        nb_drones: int
    ) -> None:
        """Print the final simulation summary.

        Args:
            total_turns: Integer number of turns used by the simulation.
            nb_drones: Integer number of delivered drones.

        Returns:
            None.
        """
        green = self.get_ansi("green")
        yellow = self.get_ansi("yellow")

        print(
            f"\n{yellow}{nb_drones}"
            f"{green} drone(s) delivered in "
            f"{yellow}{total_turns}"
            f"{green} turn(s).{self.RESET}"
        )
