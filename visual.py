from colorama import Fore, Style, init
from graph import Graph

init(autoreset=True)

COLOR_MAP: dict[str, str] = {
    "red":     Fore.RED,
    "green":   Fore.GREEN,
    "blue":    Fore.BLUE,
    "yellow":  Fore.YELLOW,
    "cyan":    Fore.CYAN,
    "magenta": Fore.MAGENTA,
    "white":   Fore.WHITE,
    "orange":  Fore.YELLOW,
    "violet":  Fore.MAGENTA,
    "gray":    Fore.WHITE,
    "rainbow": Fore.CYAN,
}


def zone_color(zone_name: str, graph: Graph) -> str:
    """Return terminal color for a zone based on its map color."""
    zone = graph.zones.get(zone_name)
    if zone and zone.color and zone.color.lower() in COLOR_MAP:
        return COLOR_MAP[zone.color.lower()]
    return Fore.WHITE


def print_turn(turn: int, moves: str, graph: Graph) -> None:
    """Print one turn — each token colored by its destination zone."""
    print(f"Turn {turn:>3}: ", end="")
    for token in moves.split():
        dash = token.index("-")
        zone_name = token[dash + 1:]
        color = zone_color(zone_name, graph)
        print(f"{color}{token}{Style.RESET_ALL}  ", end="")
    print()


def print_summary(total_turns: int, nb_drones: int) -> None:
    """Print final summary."""
    print(f"\n{Fore.GREEN}✓ {nb_drones} drone(s) delivered in "
          f"{Fore.YELLOW}{total_turns}{Fore.GREEN} turn(s).{Style.RESET_ALL}")
