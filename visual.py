from colorama import Fore, Style, init

init(autoreset=True)

ZONE_COLORS: dict[str, str] = {
    "normal":     Fore.WHITE,
    "restricted": Fore.RED,
    "priority":   Fore.GREEN,
    "blocked":    Fore.BLACK,
    "start":      Fore.CYAN,
    "end":        Fore.YELLOW,
}

DRONE_COLORS: list[str] = [
    Fore.MAGENTA,
    Fore.BLUE,
    Fore.CYAN,
    Fore.GREEN,
    Fore.YELLOW,
]


def drone_color(drone_id: int) -> str:
    """Return a consistent color for a given drone ID."""
    return DRONE_COLORS[(drone_id - 1) % len(DRONE_COLORS)]


def print_turn(turn: int, moves: str) -> None:
    """Print one simulation turn with colored drone labels."""
    print(f"{Fore.WHITE}Turn {turn:>3}: ", end="")

    for token in moves.split():
        # token looks like D1-roof1 or D2-hub-goal
        dash = token.index("-")
        drone_part = token[:dash]        # e.g. D1
        zone_part  = token[dash + 1:]   # e.g. roof1

        drone_id = int(drone_part[1:])
        color = drone_color(drone_id)
        print(f"{color}{drone_part}{Fore.WHITE}-{Fore.CYAN}{zone_part}  ",
              end="")

    print(Style.RESET_ALL)


def print_summary(total_turns: int, nb_drones: int) -> None:
    """Print a short summary after the simulation ends."""
    print(
        f"\n{Fore.GREEN}✓ All {nb_drones} drone(s) delivered "
        f"in {Fore.YELLOW}{total_turns}{Fore.GREEN} turn(s).{Style.RESET_ALL}"
    )
