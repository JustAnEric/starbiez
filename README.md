# StarbieZ (star-beez)

[![](images/Screenshot%202026-10-06%20135725.v1.png)](images/Screenshot%202026-10-06%20135725.v1.png)

Starbiez is a redo of the [Starbie](https://github.com/SharKingStudios/Starbie), and boy it packs *serious* power!

You're now getting your own extendible Tamagotchi that can run MANY things, basically sort of like a *Flipper Zero Nano* but without the pentesting tools! (don't go hacking things around town with this... :C)

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

## The process of building
### Day 1!

I spent the whole day, and I quite probably went past 4 hours (the actual making time of my board) to include the things that would make it my own...

You can see the **timestamps in the screenshot names**, for journal purposes I didn't replace them with a generic name throughout my processes!

How to interpret them:

* Example: `Screenshot 2026-10-06 064450.png`
* `2026-`: The year
* `10-`: The month
* `06`: The day
* `064450`:
    * `06`: The hour of the day (in AEST/AEDT, since I'm working on it in Australia/Sydney!)
    * `44`: The minute of the hour `06`
    * `50`: The seconds the screenshot was taken at

Hope this helps!

1. I created the project and crafted the schematic from the [tutorial](https://github.com/SharKingStudios/Starbie)

    ![](images/Screenshot%202026-10-06%20060906.png)


2. I laid out my PCB, creating the star `Edge.Cuts` from a reference image I found on Google first

    ![](images/steps/2/Screenshot%202026-10-06%20064450.png)
    ![](images/steps/2/Screenshot%202026-10-06%20071124.png)

    and then the satisfying ground layer by the B button...
    ![](images/steps/2/Screenshot%202026-10-06%20072938.png)

    Those steps took about 4 hours and 5 minutes, timed by Google stopwatch (thanks search engine monopoly... never mind)

3. One of my first modifications was with changing the MCU from an ESP32-C3 to an ESP32-S3. My first strongest candidate.

    ![](images/steps/3/Screenshot%202026-10-06%20080426.png)

    This swap didn't take very long... They're very structurally similar. I made sure to check Seeed's official guides though, just in case I got the pinouts wrong.

4. I included a second sensor, the LDR03 (light-dependent resistor is what LDR stands for) and I made sure to include a fixed resistance of 10kΩ, though this would change later down the track in my realisation an LDR03 is VERY hard to source in the real world today...!

    ![](images/steps/4/Screenshot%202026-10-06%20084634.png)

    Here's where I put it, on the right wing of the star :)

    ![](images/steps/4/Screenshot%202026-10-06%20092053.png)

    ![](images/steps/4/Screenshot%202026-10-06%20092112.png)

5. A lot of organisation, and another output was added! A buzzer or a piezo was inspired by the Sprig's design when I made my Columns game for them (still waiting for approval), and I feel this Tamagotchi would do *really* well with a bit of tunes.

    ![](images/steps/5/Screenshot%202026-10-06%20101207.png)
    ![](images/steps/5/Screenshot%202026-10-06%20100141.png)

    I put in a little resistor to prevent any surge back to the tiny ESP... yeah it's pretty small.

    ![](images/steps/5/Screenshot%202026-10-06%20101612.png)

6. I found a honeycomb SVG on Flaticon and I decided to use it for the two bottom corners of the board to add some more decoration!

    ![](images/steps/6/Screenshot%202026-10-06%20135725.png)

    This was also the time I figured out how to get the 3D models into the footprints, I spent a long time trying to figure out how to get into the footprint editor...

7. Realizing there was not enough clearance for poor Switch 3 around J2, I had to make a few changes. And these changes would be for the better, it's now a dev board... :P It's when I made the switch to the ESP32-S3 Plus to get more GPIO. This is when my board started to look a lot more like trace spaghetti, but it's okay... (I am guessing)

    ![](images/steps/7/Screenshot%202026-10-07%20000431.png)

    ![](images/steps/7/Screenshot%202026-10-06%20235611.png)

    ![](images/steps/7/Screenshot%202026-10-06%20235327.png)

    Now there's odd-even 2x8 GPIO female pins on the board, featuring these that go to the ESP32-S3 Plus! Go from right to left if you flip the Starbiez on it's right side:

    | Pin | GPIO |
    |-----|------|
    | 1 (right) | D6 |
    | 2 (left) | D7 |
    | 3 (right) | D10 |
    | 4 (left) | D11 |
    | 5 (right) | D12 |
    | 6 (left) | D13 |
    | 7 (right) | D14 |
    | 8 (left) | D15 |
    | 9 (right) | D16 |
    | 10 (left) | D17 |
    | 11 (right) | SDA (for I2C!) |
    | 12 (left) | D18 |
    | 13 (right) | SCL (for I2C!) |
    | 14 (left) | D19 |
    | 15 (right) | 3V3 output, make sure not to draw too much! |
    | 16 (left) | board GND |

    <details>
    <summary>Pin reference image for you nerds...</summary>

    > ## Front
    >
    > [![](https://files.seeedstudio.com/wiki/SeeedStudio-XIAO-ESP32S3/img/XIAO_ESP32-S3_Plus_front_pinout.png)](https://files.seeedstudio.com/wiki/SeeedStudio-XIAO-ESP32S3/img/XIAO_ESP32-S3_Plus_front_pinout.png)
    >
    > ## Back
    > [![](https://files.seeedstudio.com/wiki/SeeedStudio-XIAO-ESP32S3/img/XIAO_ESP32-S3_Plus_back_pinout.png)](https://files.seeedstudio.com/wiki/SeeedStudio-XIAO-ESP32S3/img/XIAO_ESP32-S3_Plus_back_pinout.png)

    </details>

    ![](images/steps/7/Screenshot%202026-10-07%20001022.png)

    (*sparkles*!!) The sparkles I got from Claude, I asked it to make a flat monochrome white sparkle SVG graphic I could use... I plastered it onto the board on all the corners.

8. Around this time, I was searching for good parts to use on AliExpress, but I found that shipping from China is a *little* bit too expensive for the grant I'm receiving. I then got a little distracted, still worrying myself about whether the light-dependent resistor I've wired up would be correct. More research got me to change it to a generic one, so here's the LDR part I recommend if anyone tries to build this project:

    | Specification | Value |
    |---------------|-------|
    | dark resistance (pitch black, 0 lux) | ~10MΩ |
    | light resistance (10 lux) | 8kΩ to 20kΩ |
    | max dissipation | 100mW
    | form factor | THT ~5mm |
    | ideally... | the GL5528 |

    I also switched the fixed resistance to 100kΩ so the ESP32-S3 Plus receives a more controlled value than in **0.03 V** or completely uncharted territory...

    ![](images/steps/8/Screenshot%202026-10-07%20083004.png)

    ![](images/steps/8/Screenshot%202026-10-07%20090323.png)

this took me the ENTIRETY of yesterday to build it and some of today to refine it, in retrospect I got up really early some days :| it took me about 1 hour and 22 minutes to write this writeup, according to Hackatime. I hope every viewer likes this project of mine!

## Software

I extended/am extending CircuitPython for this project for providing user access to an API, you can view my extensions to CircuitPython [here](https://github.com/JustAnEric/starbiez-circuitpython)! It's recommended to use this instead of normal CircuitPython on your ESP32-S3, as you probably won't have access to much easy modifications.

## Ending README

hopefully Hack Club likes this little project of mine, so I can keep developing it more and more... I'm definitely pushing boundaries here with what can be done but...