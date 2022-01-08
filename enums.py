"""
Useful abstractions for the existing environment.
"""
from enum import Enum


class LightStatus(Enum):
    RED = 0
    YELLOW = 1
    GREEN = 2


class Directions(Enum):
    """Directions with a displacement that works in a natural coordinate system"""
    UP = (0, 1)
    LF = (-1, 0)
    RH = (1, 0)
    DW = (0, -1)


class RawDirections(Enum):
    """The displacement is already tweaked to work with a matrix of the form [row][col]"""
    UP = (-1, 0)
    LF = (0, -1)
    RH = (0, 1)
    DW = (1, 0)
