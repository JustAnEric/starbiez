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
    def __new__(cls, x: float, y: float, z: float):
        return super().__new__(cls, (x, y, z))

    @property
    def x(self): return self[0]
    
    @property
    def y(self): return self[1]
    
    @property
    def z(self): return self[2]

class PetReaction:
    NAP_REACTION = 0
    RUN_REACTION = 1
    JUMP_REACTION = 2
    HEART_REACTION = 3