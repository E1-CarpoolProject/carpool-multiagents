from enum import Enum


class LightStatus(Enum):
    RED = 0
    YELLOW = 1
    GREEN = 2


class Directions(Enum):
    """
    THE displacement is already tweaked to work with a matrix of the form [row][col]
    1) z, 2) -z, 3) x, 4) -x (z=y)

         z
         |
    -x -- -- x
         |
         -z

        _______|2   |________
                     4
        _____3_     ________
               |   1|
    """
    UP = (-1, 0)
    LF = (0, -1)
    RH = (0, 1)
    DW = (1, 0)

