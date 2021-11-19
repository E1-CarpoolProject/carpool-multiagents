from enum import Enum


class LightStatus(Enum):
    RED = 0
    YELLOW = 1
    GREEN = 2


class IntersectionDirection(Enum):
    """
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

