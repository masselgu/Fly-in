import matplotlib.colors as mcolors
from graph import Graph

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


def get_ansi(color_name: str) -> str:
    """Convert a color name to ANSI 24-bit true color escape code."""
    try:
        r, g, b = (int(c * 255) for c in mcolors.to_rgb(color_name))
        return f"\033[38;2;{r};{g};{b}m"
    except ValueError:
        return "\033[97m"


def apply_color(text: str, color_name: str) -> str:
    """Apply color to text, with special rainbow handling."""
    if color_name.lower() == "rainbow":
        result = ""
        for i, char in enumerate(text):
            rgb = RAINBOW_COLORS[i % len(RAINBOW_COLORS)]
            r, g, b = (int(c * 255) for c in rgb)
            result += f"\033[38;2;{r};{g};{b}m{char}{RESET}"
        return result
    return f"{get_ansi(color_name)}{text}{RESET}"


def zone_color_name(zone_name: str, graph: Graph) -> str:
    """Return the color name of a zone or empty string if none."""
    zone = graph.zones.get(zone_name)
    if zone and zone.color:
        return zone.color
    return ""


def print_turn(moves: str, graph: Graph) -> None:
    """Print one turn — each token colored by its destination zone."""
    for token in moves.split():
        dash = token.index("-")
        drone_id = token[:dash]
        rest = token[dash + 1:]

        last_dash = rest.rfind("-")
        if last_dash != -1 and rest[last_dash + 1:] in graph.zones \
                and rest[:last_dash] in graph.zones:
            zone1 = rest[:last_dash]
            zone2 = rest[last_dash + 1:]
            c1 = zone_color_name(zone1, graph)
            c2 = zone_color_name(zone2, graph)
            colored1 = apply_color(zone1, c1) if c1 else zone1
            colored2 = apply_color(zone2, c2) if c2 else zone2
            print(f"{drone_id}-{colored1}-{colored2} ", end="")
        else:
            c = zone_color_name(rest, graph)
            colored = apply_color(rest, c) if c else rest
            print(f"{drone_id}-{colored} ", end="")
    print()


def print_summary(total_turns: int, nb_drones: int) -> None:
    """Print final summary."""
    g = get_ansi("green")
    y = get_ansi("yellow")
    print(f"\n{g}✓ {y}{nb_drones}{g} drone(s) delivered in "
          f"{y}{total_turns}{g} turn(s).{RESET}")
