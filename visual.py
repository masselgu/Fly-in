from graph import Graph

RESET = "\033[0m"

COLOR_MAP: dict[str, str] = {
    "red":    "\033[91m",
    "blue":   "\033[94m",
    "green":  "\033[92m",
    "white":  "\033[97m",
    "purple": "\033[95m",
    "yellow": "\033[93m",
    "orange": "\033[38;5;214m",
    "pink":   "\033[38;5;213m",
    "gray":   "\033[38;5;245m",
}


def zone_color(zone_name: str, graph: Graph) -> str:
    """Return terminal color for a zone based on its map color."""
    zone = graph.zones.get(zone_name)
    if zone and zone.color and zone.color.lower() in COLOR_MAP:
        return COLOR_MAP[zone.color.lower()]
    return "\033[97m"


def print_turn(moves: str, graph: Graph) -> None:
    """Print one turn — each token colored by its destination zone."""
    for token in moves.split():
        dash = token.index("-")
        zone_name = token[dash + 1:]
        color = zone_color(zone_name, graph)
        print(f"{color}{token}{RESET} ", end="")
    print()


def print_summary(total_turns: int, nb_drones: int) -> None:
    """Print final summary."""
    g = COLOR_MAP["green"]
    y = COLOR_MAP["yellow"]
    print(f"\n{g}✓ {y}{nb_drones}{g} drone(s) delivered in "
          f"{y}{total_turns}{g} turn(s).{RESET}")
