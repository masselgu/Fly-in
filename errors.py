class FlyInError(Exception):
    """Define the base error for project exceptions."""
    pass


class ZoneError(FlyInError):
    """Define an error raised for invalid zone data."""
    pass


class GraphError(FlyInError):
    """Define an error raised for invalid graph structure."""
    pass


class ParserError(FlyInError):
    """Define an error raised for invalid map parsing."""
    pass
