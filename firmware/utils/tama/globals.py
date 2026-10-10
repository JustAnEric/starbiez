from utils.tama._types import MenuItem, PetReaction
from typing import Literal

### EDIT THESE ###

USE_DHT = True  # selected as true for most starbiez boards
DHT_PIN = 1  # gpio pin

# hints for YOUR configurability:
#* AM2301 is the DHT21
#* AM2302 is the DHT22
DHT_TYPE: Literal['dht11', 'dht21', 'dht22'] = "dht22" # you'll need a DHT with the traditional 4-pinout: VCC-DATA-X-GND

I2C : dict[str, int] = {
    "OLED_ADDRESS": 0x3c,
    "MPU6050_ADDRESS": 0x68,

    # gpio pins
    "SDA_PIN": 5,
    "SCL_PIN": 6,
}

BUTTON : dict[str, int] = {
    "BUTTON_ONE_PIN":   2,
    "BUTTON_TWO_PIN":   3,
    "BUTTON_THREE_PIN": 4,
}

# starting stats
STARTING_JOY = 70
STARTING_ENERGY = 75
STARTING_FULLNESS = 65

MENU_ITEMS : list[MenuItem] = [
    MenuItem(label="NAP", joyChange=1, energyChange=18, fullnessChange=-4, reaction=PetReaction.NAP_REACTION),
    MenuItem(label="PLAY", joyChange=12, energyChange=-9, fullnessChange=-5, reaction=PetReaction.RUN_REACTION),
    MenuItem(label="FEED", joyChange=3, energyChange=2, fullnessChange=18, reaction=PetReaction.JUMP_REACTION),
    MenuItem(label="PET", joyChange=7, energyChange=0, fullnessChange=0, reaction=PetReaction.HEART_REACTION),
]

MENU_ITEM_COUNT = len(MENU_ITEMS)
MENU_TILT_LIMIT = 6.0

# useful settings for MPU
SWAP_MPU_AXES = False
MENU_X_DIRECTION = 1.0
MENU_Y_DIRECTION = -1.0

MENU_CENTER_DEADZONE = 0.8
SHAKE_THRESHOLD = 7.0

SHAKE_JOY_CHANGE = 5
SHAKE_ENERGY_CHANGE = -2
SHAKE_FULLNESS_CHANGE = -1

PET_SPRITE_WIDTH = 32
PET_SPRITE_HEIGHT = 32

PET_WALK_PIXEL_MS = 70
PET_PRE_JUMP_MS = 230
PET_JUMP_MS = 430
PET_JUMP_HEIGHT = 16
NAP_DURATION_MS = 48000
HEARTS_DURATION_MS = 1600
PLAY_LAP_MS = 800
PLAY_LAP_COUNT = 1

SCREEN_WIDTH = 128
SCREEN_HEIGHT = 64
MENU_CENTER_X = 64
MENU_CENTER_Y = 32
MENU_ITEM_X = [64, 108, 64, 20]
MENU_ITEM_Y = [12, 32,  53, 32]
MENU_BALL_X_RANGE = 37
MENU_BALL_Y_RANGE = 22
BUTTON_DEBOUNCE_MS = 30
MPU_READ_INTERVAL_MS = 30
DHT_READ_INTERVAL_MS = 2220
SHAKE_COOLDOWN_MS = 650
STANDARD_GRAVITY = 9.80665


### DON'T EDIT BELOW! ###