from collections import namedtuple

MenuItem = namedtuple('MenuItem', [
    'label', 'joyChange', 'energyChange',
    'fullnessChange', 'reaction'
])

PetState = namedtuple('PetState', [
    'joy', 'energy', 'fullness'
])

ButtonState = namedtuple('ButtonState', [
    'pin', 'stableState',
    'lastRawState', 'lastChangedAt',
    'realButton'
])

class Axis3(tuple):
    def __init__(self, x: float, y: float, z: float):
        super(tuple).__init__([x, y, z])
        self.x = x
        self.y = y
        self.z = z