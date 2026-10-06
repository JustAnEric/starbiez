# StarbieZ (star-beez)

[![](images/Screenshot%202026-10-06%20135725.v1.png)](images/Screenshot%202026-10-06%20135725.v1.png)

Starbiez is a redo of the [Starbie](https://github.com/SharKingStudios/Starbie), and boy it packs *serious* power!

You're now getting your own extendable Tamagotchi that can run MANY things, basically sort of like a *Flipper Zero Nano* but without the pentesting tools! (don't go hacking things around town with this... :C)

## What it does

the ESP32-S3 Plus is where I'd start the shift from MCU to CPU, and it's the main driver for this project. With 16 MB of flash and 8 MB of RAM, it's way more than all the classic Tamagotchis that had **1 KB of RAM and ROM**! this Starbie is equipped with greater environmental awareness, audio and just *one more* button that adds so many more possibilities for what can be done with this project.

the environment can be currently measured by these sensors:

* a light dependent resistor on the right front face of the board
* a DHT11 humidity sensor on the top front face of the board
* AND a 6 pin IMU called the MPU6050 at the bottom right of the board!

the outputs on this device are *pretty simple*:
* 128x64 SSD1306 OLED screen
* buzzer/piezo

you provide input to this project by literally just clicking the cherry MX keyboard switches... and the circuitpython software being packaged for this project is considerably extendable being based off of the C++/.INO software. (yes, I'm rewriting/have rewritten it to make it easier for extensions, welcome beginners!)

## Ending README

hopefully Hack Club likes this little project of mine, so I can keep developing it more and more... I'm definitely pushing boundaries here but...