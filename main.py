import sys
from errors import FlyInError
from parser import Parser
from simulation import Simulation
from pathfinder import Pathfinder
from visual import Visualizer


def main() -> None:
    """Entry point: parse map, find paths, run simulation, print log.

    Reads the map file from sys.argv[1], computes drone routes,
    runs the simulation, and prints the turn-by-turn log.
    """
    try:
        if len(sys.argv) < 2:
            print("Usage: 'python3 main.py <map_file>' or "
                  "'make run FILE=<map_file>'")
            sys.exit(1)

        parser = Parser()
        parser.parse(sys.argv[1])

        graph = parser.graph
        nb_drones = parser.nb_drones
        start = parser.start_zone.name if parser.start_zone else ""
        end = parser.end_zone.name if parser.end_zone else ""

        pathfinder = Pathfinder(graph)
        routes = pathfinder.compute_k_routes(start, end)
        paths = [[zone.name for zone in route] for route in routes]

        sim = Simulation(graph, paths, nb_drones, end)
        logs = sim.run()

        visualizer = Visualizer(graph)
        for line in logs:
            visualizer.print_turn(line)

        visualizer.print_summary(len(logs), nb_drones)
    except FlyInError as e:
        print(f"Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
