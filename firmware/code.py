from utils.tama import globals, _types, sprites
from utils.starbie import is_starbie_board
from utils import logging, jerryscript_js, path, webserver
from typing import Union


import board
import digitalio
import time
import os
import math
import adafruit_ssd1306
import adafruit_framebuf
import adafruit_mpu6050
import adafruit_dht
import digitalio
import json

JSCRIPT_MODULES: list[dict] = []

class Main:
    def __init__(self):
        self.buttons: dict[_types.ButtonState, digitalio.DigitalInOut] = {}

        self.currentView : Union[str['PET_VIEW' | 'MENU_VIEW' | 'STATS_VIEW']] = ""
        self.petState : _types.PetState = _types.PetState(
            globals.STARTING_JOY, globals.STARTING_ENERGY,
            globals.STARTING_FULLNESS,
        )

        self.mpuFound = False
        self.dhtFound = False
        self.acceleration = _types.Axis3(x=0.0, y=0.0, z=globals.STANDARD_GRAVITY)
        self.temperatureC = -100000.0 # impossible in the real world
        self.humidity = -100000.0
        self.menuBall = [globals.MENU_CENTER_X, globals.MENU_CENTER_Y]
        self.menuCenterAcceleration : list[float, float] = [0.0, 0.0]
        self.selectedMenuItem = -1
        self.lastMpuReadAt = 0.0
        self.lastDhtReadAt = 0.0
        self.lastShakeAt = 0.0
        self.shakeAnimationEndsAt = 0.0
        self.petJumpStartedAt = 0.0
        self.nappingUntil = 0.0
        self.heartAnimationEndsAt = 0.0
        self.playRunStartedAt = 0.0
        self.nappingPetX = 0

        self.i2c = board.I2C()

        try:
            logging.msg_boot(f"using {globals.SCREEN_WIDTH}x{globals.SCREEN_HEIGHT} display on address {hex(globals.I2C.get("OLED_ADDRESS", 0x3C))} ({globals.I2C.get("OLED_ADDRESS", 0x3C)})")

            self.DISPLAY = adafruit_ssd1306.SSD1306_I2C(
                width=globals.SCREEN_WIDTH, 
                height=globals.SCREEN_HEIGHT, 
                i2c=self.i2c,
                addr=globals.I2C.get("OLED_ADDRESS", 0x3C)
            )
            self.DISPLAY.poweron()
            self.DISPLAY.fill(0)
        except:
            logging.msg_err("could not connect to display!!!")
            self.DISPLAY = None
            exit(3)

        try:
            logging.msg_boot(f"using MPU6050 IMU on address {hex(globals.I2C.get("MPU6050_ADDRESS", 0x68))} ({globals.I2C.get("MPU6050_ADDRESS", 0x68)})")

            self.MPU = adafruit_mpu6050.MPU6050(
                i2c_bus=self.i2c, 
                address=globals.I2C.get("MPU6050_ADDRESS", 0x68)
            )
            self.MPU.accelerometer_range = adafruit_mpu6050.Range.RANGE_8_G
            self.MPU.gyro_range = adafruit_mpu6050.GyroRange.RANGE_500_DPS
            self.MPU.filter_bandwidth = adafruit_mpu6050.Bandwidth.BAND_21_HZ
            self.mpuFound = True
        except:
            logging.msg_err("could not connect to MPU6050 IMU!!!")
            self.MPU = None
            self.mpuFound = False
            exit(3)


        if globals.USE_DHT:
            try:
                if globals.DHT_TYPE == "dht11":
                    logging.msg_boot(f"using DHT11 on pin {globals.DHT_PIN or 1}")

                    self.DHT = adafruit_dht.DHT11(
                        pin=globals.DHT_PIN or 1
                    )
                    self.dhtFound = True
                elif globals.DHT_TYPE == "dht21":
                    logging.msg_boot(f"using DHT21 on pin {globals.DHT_PIN or 1}")
                    
                    self.DHT = adafruit_dht.DHT21(
                        pin=globals.DHT_PIN or 1
                    )
                    self.dhtFound = True
                elif globals.DHT_TYPE == "dht22":
                    logging.msg_boot(f"using DHT22 on pin {globals.DHT_PIN or 1}")
                    
                    self.DHT = adafruit_dht.DHT22(
                        pin=globals.DHT_PIN or 1
                    )
                    self.dhtFound = True
                else:
                    logging.msg_warn(f"DHT was enabled but it seems you did not configure a DHT_TYPE value! On the common Starbiez, this value is just the 'dht22' if that helps. ({globals.DHT_PIN or 1})")
                    self.DHT = None
                    self.dhtFound = False
            except:
                logging.msg_warn(f"DHT was enabled but we could not find one connected to the pin selected! ({globals.DHT_PIN or 1})")
                self.DHT = None
                self.dhtFound = False
        else:
            logging.msg_boot(f"DHT was explicitly disabled, not loading")
            self.DHT = None
            self.dhtFound = False

    def load_pet(self):
        if path.exists(path="./user-data.json"):
            with open("./user-data.json", "r") as fp:
                pets_data = json.load(fp)
                fp.close()
            self.petState.joy = pets_data.get('starbie',{}).get('joy', globals.STARTING_JOY)
            self.petState.energy = pets_data.get('starbie',{}).get('energy', globals.STARTING_ENERGY)
            self.petState.fullness = pets_data.get('starbie',{}).get('fullness', globals.STARTING_FULLNESS)
        else:
            # file doesn't exist
            payload = {
                'starbie': {
                    'joy': globals.STARTING_JOY,
                    'energy': globals.STARTING_ENERGY,
                    'fullness': globals.STARTING_FULLNESS
                }
            }
            with open("./user-data.json", "w") as fp:
                json.dump(payload, fp, indent=4)
            self.petState.joy = payload.get('starbie').get('joy')
            self.petState.energy = payload.get('starbie').get('energy')
            self.petState.fullness = pets_data.get('starbie').get('fullness')

    def save_pet(self):
        payload = {
            'starbie': {
                'joy': self.petState.joy,
                'energy': self.petState.energy,
                'fullness': self.petState.fullness
            }
        }
        with open("./user-data.json", "w") as fp:
            json.dump(payload, fp, indent=4)

    def change_pet(self, joyChange: int, energyChange: int, fullnessChange: int):
        self.petState.joy = self.constrain(self.petState.joy + joyChange, 0, 100)
        self.petState.energy = self.constrain(self.petState.energy + energyChange, 0, 100)
        self.petState.fullness = self.constrain(self.petState.fullness + fullnessChange, 0, 100)
        self.save_pet()

    def add_button(self, pin: int):
        button = digitalio.DigitalInOut(pin=pin)
        button.direction = digitalio.Direction.INPUT
        button.pull = button.pull.UP
        buttonState = _types.ButtonState(
            pin=pin, 
            stableState=button.value, 
            lastRawState=button.value, 
            lastChangedAt=time.time(),
            realButton=button
        )
        self.buttons[buttonState] = button

    def get_button(self, pin: int) -> _types.ButtonState | None:
        for button in self.buttons:
            if button.pin == pin:
                return button
        return None

    def was_button_pressed(self, button: _types.ButtonState):
        rawState = button.realButton.value
        now = time.time()
        if rawState != button.lastRawState:
            button.lastRawState = rawState
            button.lastChangedAt = now
        if (rawState != button.stableState and now - button.lastChangedAt >= self._ms_to_s(globals.BUTTON_DEBOUNCE_MS)):
            button.stableState = rawState
            return button.stableState == False
        return False

    def _ms_to_s(self, v: int):
        return v/1000

    def update_mpu(self):
        now = time.time()
        if (not self.mpuFound or not self.MPU) or (now - self.lastMpuReadAt < self._ms_to_s(globals.MPU_READ_INTERVAL_MS)):
            return
        self.lastMpuReadAt = now
        accel = self.MPU.acceleration
        self.acceleration = _types.Axis3(x=accel[0], y=accel[1], z=accel[2])

    def update_dht(self):
        now = time.time()
        if (not self.dhtFound or not self.DHT) or (now - self.lastDhtReadAt < self._ms_to_s(globals.DHT_READ_INTERVAL_MS)):
            return
        self.lastDhtReadAt = now
        try:
            self.humidity = self.DHT.humidity
            self.temperatureC = self.DHT.temperature
        except RuntimeError:
            logging.msg_warn("mild error while updating DHT stats")
            pass

    def pet_walking_x(self, now: float):
        """
        `now` should be in seconds
        """
        farthestX = globals.SCREEN_WIDTH - globals.PET_SPRITE_WIDTH
        roundTrip = farthestX * 2
        step = (now / self._ms_to_s(globals.PET_WALK_PIXEL_MS)) % roundTrip
        return step if step <= farthestX else roundTrip - step

    def play_run_duration(self) -> float:
        """
        in seconds
        """
        return self._ms_to_s(globals.PLAY_LAP_MS) * globals.PLAY_LAP_COUNT

    def is_napping(self) -> bool:
        return self.nappingUntil != 0 and time.time() < self.nappingUntil

    def is_playing(self) -> bool:
        return self.playRunStartedAt != 0 and time.time() - self.playRunStartedAt < self.play_run_duration()

    def play_run_x(self, now: float):
        """
        `now` should be in seconds
        """
        farthestX = globals.SCREEN_WIDTH - globals.PET_SPRITE_WIDTH
        lapAge = (now - self.playRunStartedAt) % self._ms_to_s(globals.PLAY_LAP_MS)
        progress = lapAge / self._ms_to_s(globals.PLAY_LAP_MS)
        return int(progress * 2.0 * farthestX) if progress < 0.5 else int((1.0 - progress) * 2.0 * farthestX)

    def update_pet_timers(self):
        if self.nappingUntil != 0 and not self.is_napping():
            self.nappingUntil = 0
        if self.playRunStartedAt != 0 and not self.is_playing():
            self.playRunStartedAt = 0

    def constrain(self, val: float, minv: float, maxv: float):
        return max(minv, min(val, maxv))

    def update_menu_ball(self):
        xTilt = self.acceleration.x - self.menuCenterAcceleration[0]
        yTilt = self.acceleration.y - self.menuCenterAcceleration[1]
        if globals.SWAP_MPU_AXES:
            oldXTilt = xTilt
            xTilt = yTilt
            yTilt = oldXTilt
        xTilt = self.constrain(xTilt * globals.MENU_X_DIRECTION, -globals.MENU_TILT_LIMIT, globals.MENU_TILT_LIMIT)
        yTilt = self.constrain(yTilt * globals.MENU_Y_DIRECTION, -globals.MENU_TILT_LIMIT, globals.MENU_TILT_LIMIT)
        targetX = globals.MENU_CENTER_X + (xTilt / globals.MENU_TILT_LIMIT) * globals.MENU_BALL_X_RANGE
        targetY = globals.MENU_CENTER_Y + (yTilt / globals.MENU_TILT_LIMIT) * globals.MENU_BALL_Y_RANGE

        menuBallX += (targetX - menuBallX) * 0.20
        menuBallY += (targetY - menuBallY) * 0.20

        fbfXTilt = abs(xTilt)
        fbfYTilt = abs(yTilt)

        if fbfXTilt < globals.MENU_CENTER_DEADZONE and fbfYTilt < globals.MENU_CENTER_DEADZONE:
            self.selectedMenuItem = -1
        elif fbfXTilt > fbfYTilt:
            self.selectedMenuItem = 1 if xTilt > 0.0 else 3 # r or l
        else:
            self.selectedMenuItem = 2 if yTilt > 0.0 else 0 # b or t

    def check_for_shake(self):
        if (not self.mpuFound or not self.MPU) or self.currentView != 'PET_VIEW':
            return

        mag = self.sqrtf(self.acceleration.x * self.acceleration.x +
                         self.acceleration.y * self.acceleration.y +
                         self.acceleration.z * self.acceleration.z)
        now = time.time()
        if abs(mag - globals.STANDARD_GRAVITY) >= globals.SHAKE_THRESHOLD and now - self.lastShakeAt >= self._ms_to_s(globals.SHAKE_COOLDOWN_MS):
            self.lastShakeAt = now
            self.nappingUntil = 0
            self.shakeAnimationEndsAt = now + 350
            self.change_pet(globals.SHAKE_JOY_CHANGE, globals.SHAKE_ENERGY_CHANGE, globals.SHAKE_FULLNESS_CHANGE)
            self.save_pet()

    def open_menu(self):
        self.currentView = "MENU_VIEW"
        self.selectedMenuItem = -1
        self.menuBall[0] = globals.MENU_CENTER_X
        self.menuBall[1] = globals.MENU_CENTER_Y
        self.menuCenterAcceleration[0] = self.acceleration.x
        self.menuCenterAcceleration[1] = self.acceleration.y

    def choose_menu_item(self):
        if self.selectedMenuItem == -1:
            return

        item = globals.MENU_ITEMS[self.selectedMenuItem]
        self.change_pet(item.joyChange, item.energyChange, item.fullnessChange)
        self.save_pet()
        now = time.time()
        self.nappingUntil = 0
        self.heartAnimationEndsAt = 0
        self.playRunStartedAt = 0

        if item.reaction == _types.PetReaction.NAP_REACTION:
            self.petJumpStartedAt = 0
            self.nappingPetX = self.pet_walking_x(now=now)
            self.nappingUntil = now + self._ms_to_s(globals.NAP_DURATION_MS)
        elif item.reaction == _types.PetReaction.RUN_REACTION:
            self.petJumpStartedAt = 0
            self.playRunStartedAt = now
            self.heartAnimationEndsAt = now + self.play_run_duration()
        else:
            self.petJumpStartedAt = now
            if item.reaction == _types.PetReaction.HEART_REACTION:
                self.heartAnimationEndsAt = now + self._ms_to_s(globals.HEARTS_DURATION_MS)
        
        self.currentView = "PET_VIEW"

    def handle_buttons(self):
        button1 = self.get_button(pin=globals.BUTTON.get("BUTTON_ONE_PIN", 2))
        button2 = self.get_button(pin=globals.BUTTON.get("BUTTON_TWO_PIN", 3))

        if self.was_button_pressed(button=button1):
            if self.currentView == "MENU_VIEW":
                self.choose_menu_item()
            else:
                self.open_menu()

        if self.was_button_pressed(button=button2):
            self.currentView = "PET_VIEW" if self.currentView == "STATS_VIEW" else "STATS_VIEW"

    def draw_heart(self, x: int, y: int):
        SSD1306_WHITE = 1
        self.DISPLAY.fill_rect(x - 2, y, 2, 2, SSD1306_WHITE)
        self.DISPLAY.fill_rect(x + 1, y, 2, 2, SSD1306_WHITE)
        self.DISPLAY.fill_rect(x - 3, y + 2, 7, 2, SSD1306_WHITE)
        self.DISPLAY.fill_rect(x - 2, y + 4, 5, 1, SSD1306_WHITE)
        self.DISPLAY.fill_rect(x - 1, y + 5, 3, 1, SSD1306_WHITE)
        self.DISPLAY.pixel(x, y + 6, SSD1306_WHITE)

    def draw_hearts(self, now: float, petX: int, petY: int):
        """
        `now` in seconds
        """
        if now >= self.heartAnimationEndsAt:
            return

        progress = 1.0 - (self.heartAnimationEndsAt - now) / self._ms_to_s(globals.HEARTS_DURATION_MS)
        rise = progress * 18.0
        self.draw_heart(petX + 10, petY - 3 - rise)
        self.draw_heart(petX + 22, petY - 9 - rise / 2)

    def draw_sleep_zs(self, now: float, petX: int, petY: int):
        """
        `now` in seconds
        """
        rise = (now / 300) % 15
        self.DISPLAY.text("z", petX + 23, petY - 2 - rise)
        self.DISPLAY.text("z", petX + 28, petY - 8 - rise / 2)

    def draw_pet(self):
        SSD1306_WHITE = 1
        self.DISPLAY.fill(0)
        now = time.time()
        petX = self.nappingPetX if self.is_napping() else self.pet_walking_x(now=now)
        if self.is_playing():
            petX = self.play_run_x(now=now)
        petY = globals.SCREEN_HEIGHT - globals.PET_SPRITE_HEIGHT

        if now < self.shakeAnimationEndsAt:
            petX += (math.sin(now / 18.0) * 3.0)

        if not self.is_napping() and self.petJumpStartedAt != 0:
            animationAge = now - self.petJumpStartedAt

            if animationAge < self._ms_to_s(globals.PET_PRE_JUMP_MS):
                petX += (math.sin(now / 16.0) * 3.0)
            elif animationAge < self._ms_to_s(globals.PET_PRE_JUMP_MS) + self._ms_to_s(globals.PET_JUMP_MS):
                jumpProgress = animationAge - self._ms_to_s(globals.PET_PRE_JUMP_MS) / self._ms_to_s(globals.PET_JUMP_MS)
                petY -= (math.sin(jumpProgress * math.pi) * globals.PET_JUMP_HEIGHT)
            else:
                self.petJumpStartedAt = 0

        petX = self.constrain(petX, 0, globals.SCREEN_WIDTH - globals.PET_SPRITE_WIDTH)
        asset_buf = adafruit_framebuf.FrameBuffer(
            sprites.PET_SPRITE_001,
            globals.PET_SPRITE_WIDTH, globals.PET_SPRITE_HEIGHT,
            adafruit_framebuf.MHMSBFormat
        )

        self.DISPLAY.blit(asset_buf, petX, petY, SSD1306_WHITE)

        if self.is_napping():
            self.draw_sleep_zs(now, petX, petY)
        self.draw_hearts(now, petX, petY)

    def draw_round_rect(self, x: int, y: int, w: int, h: int, r, color, fill=False):
        if r <= 0:
            if fill:
                self.DISPLAY.fill_rect(x, y, w, h, color)
            else:
                self.DISPLAY.rect(x, y, w, h, color)
            return

        # restrict maximum radius calculation to avoid distort
        r = min(r, w // 2, h // 2)

        if fill:
            # draw center block and horizontal extensions
            self.DISPLAY.fill_rect(x + r, y, w - 2 * r, h, color)
            self.DISPLAY.fill_rect(x, y + r, r, h - 2 * r, color)
            self.DISPLAY.fill_rect(x + w - r, y + r, r, h - 2 * r, color)
        else:
            # draw direct boundary edges
            self.DISPLAY.hline(x + r, y, w - 2 * r, color)          # t boundary
            self.DISPLAY.hline(x + r, y + h - 1, w - 2 * r, color)  # b boundary
            self.DISPLAY.vline(x, y + r, h - 2 * r, color)          # l boundary
            self.DISPLAY.vline(x + w - 1, y + r, h - 2 * r, color)  # r boundary

        cx, cy = r, 0
        d = 1 - r

        while cx >= cy:
            # tl corner
            self.DISPLAY.pixel(x + r - cy, y + r - cx, color)
            self.DISPLAY.pixel(x + r - cx, y + r - cy, color)
            if fill:
                self.DISPLAY.hline(x + r - cx, y + r - cy, cx, color)
                self.DISPLAY.hline(x + r - cy, y + r - cx, cy, color)

            # tr corner
            self.DISPLAY.pixel(x + w - r - 1 + cy, y + r - cx, color)
            self.DISPLAY.pixel(x + w - r - 1 + cx, y + r - cy, color)
            if fill:
                self.DISPLAY.hline(x + w - r - 1, y + r - cy, cx, color)
                self.DISPLAY.hline(x + w - r - 1, y + r - cx, cy, color)

            # bl corner
            self.DISPLAY.pixel(x + r - cy, y + h - r - 1 + cx, color)
            self.DISPLAY.pixel(x + r - cx, y + h - r - 1 + cy, color)
            if fill:
                self.DISPLAY.hline(x + r - cx, y + h - r - 1 + cy, cx, color)
                self.DISPLAY.hline(x + r - cy, y + h - r - 1 + cx, cy, color)

            # br corner
            self.DISPLAY.pixel(x + w - r - 1 + cy, y + h - r - 1 + cx, color)
            self.DISPLAY.pixel(x + w - r - 1 + cx, y + h - r - 1 + cy, color)
            if fill:
                self.DISPLAY.hline(x + w - r - 1, y + h - r - 1 + cy, cx, color)
                self.DISPLAY.hline(x + w - r - 1, y + h - r - 1 + cx, cy, color)

            cy += 1
            if d < 0:
                d += 2 * cy + 1
            else:
                cx -= 1
                d += 2 * (cy - cx) + 1

    def draw_circle(self, x0, y0, r, color, fill=False):
        # big math
        x = r
        y = 0
        err = 0

        while x >= y:
            if fill:
                # draw horizontal lines between symmetric points to fill the space
                self.DISPLAY.hline(x0 - x, y0 + y, 2 * x + 1, color)
                self.DISPLAY.hline(x0 - x, y0 - y, 2 * x + 1, color)
                self.DISPLAY.hline(x0 - y, y0 + x, 2 * y + 1, color)
                self.DISPLAY.hline(x0 - y, y0 - x, 2 * y + 1, color)
            else:
                # plot the 8 octant outline points
                self.DISPLAY.pixel(x0 + x, y0 + y, color)
                self.DISPLAY.pixel(x0 + y, y0 + x, color)
                self.DISPLAY.pixel(x0 - y, y0 + x, color)
                self.DISPLAY.pixel(x0 - x, y0 + y, color)
                self.DISPLAY.pixel(x0 - x, y0 - y, color)
                self.DISPLAY.pixel(x0 - y, y0 - x, color)
                self.DISPLAY.pixel(x0 + y, y0 - x, color)
                self.DISPLAY.pixel(x0 + x, y0 - y, color)

            y += 1
            if err <= 0:
                err += 2 * y + 1
            else:
                x -= 1
                err += 2 * (y - x) + 1

    def draw_menu_item(self, item: int):
        boxWidth = 33
        boxHeight = 12
        boxX = globals.MENU_ITEM_X[item] - boxWidth / 2
        boxY = globals.MENU_ITEM_Y[item] - boxHeight / 2
        isSelected = item == self.selectedMenuItem

        textColor = 0
        if isSelected:
            self.draw_round_rect(boxX, boxY, boxWidth, boxHeight, 3, 1)
        else:
            self.draw_round_rect(boxX, boxY, boxWidth, boxHeight, 3, 0)
            textColor = 1

        labelLength = len(globals.MENU_ITEMS[item].label)
        self.DISPLAY.text(globals.MENU_ITEMS[item].label, globals.MENU_ITEM_X[item] - labelLength * 3, globals.MENU_ITEM_Y[item] - 3, textColor)

    def draw_menu(self):
        self.DISPLAY.fill(0)
        self.DISPLAY.line(0, 0, globals.SCREEN_WIDTH - 1, globals.SCREEN_HEIGHT - 1, 1)
        self.DISPLAY.line(0, globals.SCREEN_HEIGHT - 1, globals.SCREEN_WIDTH - 1, 0, 1)

        for item in range(globals.MENU_ITEM_COUNT):
            self.draw_menu_item(item)

        self.draw_circle(globals.MENU_CENTER_X, globals.MENU_CENTER_Y, 11, 1)
        self.draw_circle(int(self.menuBall[0]), int(self.menuBall[1]), 4, 1, True)

    def draw_stat_bar(self, y: int, label: str, value: int):
        self.DISPLAY.text(label, 4, y, 1)
        self.DISPLAY.rect(48, y, 57, 8, 1)
        width = int((value * 55) / 100)
        self.DISPLAY.fill_rect(49, y + 1, width, 6, 1)
        self.DISPLAY.text(value, 109, y, 1)

    def draw_stats(self):
        self.DISPLAY.fill(0)
        self.draw_stat_bar(5, "JOY", self.petState.joy)
        self.draw_stat_bar(20, "ENERGY", self.petState.energy)
        self.draw_stat_bar(35, "FULL", self.petState.fullness)

        if self.temperatureC != -100000.0:
            self.DISPLAY.text(f"TEMP {int(self.temperatureC)}C", 4, 53, 1)
        else:
            self.DISPLAY.text(f"TEMP --", 4, 53, 1)

        if self.humidity != -100000.0:
            self.DISPLAY.text(f"H {int(self.humidity)}%", 76, 53, 1)
        else:
            self.DISPLAY.text(f"H --", 76, 53, 1)

    def draw_current_view(self):
        if self.currentView == "MENU_VIEW":
            self.draw_menu()
        elif self.currentView == "STATS_VIEW":
            self.draw_stats()
        else:
            self.draw_pet()
        self.DISPLAY.show()

if __name__ == "__main__":
    if not is_starbie_board():
        logging.msg_err("are you sure this is a starbie board?? we can't verify it is. if this is your own design of the starbie board, edit the settings.json file!")
        exit(2)

    if not jerryscript_js.is_jerryscript_available():
        logging.msg_warn("modularity was disabled... you won't be able to use the modules/ directory to write hooks on top of me!!")
        logging.msg_warn("did you manage to flash the correct firmware.uf2 file to me? (https://github.com/JustAnEric/starbiez/blob/main/firmware/README.txt)")
    else:
        if not path.exists("./modules"):
            os.mkdir("./modules")
            logging.msg_boot("no JScript modules were found to load")
        else:
            f_listing = os.listdir("./modules")
            logging.msg_boot(f"loading {len(f_listing)} JScript modules into memory...")

            for entry in f_listing:
                if not entry.lower().strip().endswith(".js"): continue
                JSCRIPT_MODULES.append({
                    "filename": entry,
                    "module": jerryscript_js.run_jscript_file(entry)
                })
                logging.msg_boot(f"  loaded {entry} successfully")
    
    logging.msg_boot("boot has finished")

    tama = Main()
    tama.add_button(globals.BUTTON.get("BUTTON_ONE_PIN",2))
    tama.add_button(globals.BUTTON.get("BUTTON_TWO_PIN",3))
    tama.add_button(globals.BUTTON.get("BUTTON_THREE_PIN",4))
    tama.load_pet()
    tama.draw_current_view()

    while True:
        tama.update_mpu()
        tama.update_dht()
        tama.update_pet_timers()
        tama.handle_buttons()

        if tama.currentView == "MENU_VIEW":
            tama.update_menu_ball()
        else:
            tama.check_for_shake()

        tama.draw_current_view()

        time.sleep(16)