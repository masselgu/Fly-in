class FlyInError(Exception):
    """Base error for all project errors"""
    pass


class ZoneError(FlyInError):
    """Error related to zone data"""
    pass


class GraphError(FlyInError):
    """Error related to graph structure"""
    pass


class ParserError(FlyInError):
    """Error related to file parsing"""
    pass
