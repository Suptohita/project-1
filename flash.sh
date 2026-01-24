#!/bin/bash

source venv/bin/activate
echo "Venv activated"

# Flash ESP32 firmware
echo "Erasing flash..."
esptool --chip esp32 --port /dev/tty.usbserial-210 erase_flash

sleep 2

echo "Writing firmware..."
esptool --chip esp32 --port /dev/tty.usbserial-210 --baud 460800 write-flash -z 0x1000 ESP32_GENERIC-20251209-v1.27.0.bin

sleep 1

# Create folders on ESP32
mpremote connect /dev/tty.usbserial-210 fs mkdir :libs
mpremote connect /dev/tty.usbserial-210 fs mkdir :games

# Copy libs files
mpremote connect /dev/tty.usbserial-210 fs cp libs/__init__.py :libs/__init__.py
mpremote connect /dev/tty.usbserial-210 fs cp libs/tcs34725.py :libs/tcs34725.py
mpremote connect /dev/tty.usbserial-210 fs cp libs/rgb_led.py :libs/rgb_led.py
mpremote connect /dev/tty.usbserial-210 fs cp libs/button.py :libs/button.py
mpremote connect /dev/tty.usbserial-210 fs cp libs/pot_dimmer.py :libs/pot_dimmer.py
mpremote connect /dev/tty.usbserial-210 fs cp libs/ili9341.py :libs/ili9341.py

# Copy games files
mpremote connect /dev/tty.usbserial-210 fs cp games/__init__.py :games/__init__.py
mpremote connect /dev/tty.usbserial-210 fs cp games/game1.py :games/game1.py
mpremote connect /dev/tty.usbserial-210 fs cp games/game2.py :games/game2.py

echo "Done!"