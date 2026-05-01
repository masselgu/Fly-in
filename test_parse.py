from parser import Parser
from pathfinder import Pathfinder
from errors import ParserError

try:
    p = Parser()
    p.parse("maps/test1.txt")

    finder = Pathfinder(p.graph)
    path = finder.find_path(
        p.start_zone.name,
        p.end_zone.name
    )

    print("Path found:")
    for zone in path:
        print(f"  → {zone.name} (cost={zone.zone_type})")

except ParserError as e:
    print(f"Error: {e}")
