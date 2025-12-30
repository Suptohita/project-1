#!/bin/bash

# Flash ESP32 firmware
echo "Erasing flash..."
esptool --chip esp32 --port /dev/tty.usbserial-210 erase_flash

sleep 2

echo "Writing firmware..."
esptool --chip esp32 --port /dev/tty.usbserial-210 --baud 460800 write-flash -z 0x1000 ESP32_GENERIC-20251209-v1.27.0.bin

echo "Done!"