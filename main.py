import sys
from parser import Parser
from pathfinder import Pathfinder
from simulation import Simulation
from visual import Visual
from errors import FlyInError


def main() -> None:
    """Entry point for the drone simulation."""
    if len(sys.argv) != 2:
        print("Usage: python main.py <map_file>")
        sys.exit(1)

    try:
        p = Parser()
        p.parse(sys.argv[1])

        finder = Pathfinder(p.graph)

        sim = Simulation(
            graph=p.graph,
            pathfinder=finder,
            start_zone=p.start_zone,
            end_zone=p.end_zone,
            nb_drones=p.nb_drones
        )

        logs = sim.run()
        Visual.display(logs, p.graph, p.nb_drones)

    except FlyInError as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
