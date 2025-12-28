# Color Mixing Game

A MicroPython project for ESP32 that implements an interactive color mixing game using a TCS34725 color sensor and an RGB LED.

## 🛠 Hardware Requirements

- ESP32 microcontroller
- TCS34725 color sensor
- RGB LED (common cathode or anode)
- Ili9341 LCD display
- Connecting wires and breadboard

### Wiring Diagram

## 📦 Software Setup

### Prerequisites
- Python 3.x installed on your computer
- MicroPython firmware for ESP32
- mpremote tool for uploading code
- VSCode (Preferably)

### Installation Steps
1. **Install esptool:**
    ```
    pip install esptool
   ```

2. **Flash MicroPython to ESP32:**
   - Download the latest MicroPython firmware for ESP32 from [micropython.org](https://micropython.org/download/esp32/)
   - Use esptool to flash the firmware:
     ```
     esptool --chip esp32 --port /dev/tty.usbserial-xxx erase_flash
     esptool --chip esp32 --port /dev/tty.usbserial-xxx --baud 460800 write_flash -z 0x1000 esp32-xxx.bin
     ```

3. **Install mpremote:**
   ```
   pip install mpremote
   ```

## 🚀 Usage

1. **Upload the code:**
   - Use the VS Code tasks provided (cmd+shift+p > run tasks):
     - "Upload main.py": Uploads the main script
     - "Upload libs": Uploads the libraries folder
     - "Upload & Reset": Uploads everything and resets the ESP32
     - "Reset ESP32": Resets the device
     - "Open REPL": Opens the MicroPython REPL for debugging


## 📁 Project Structure

```
colorMixingGame/
├── main.py          # Main game script
├── libs/            # MicroPython libraries
├── README.md        # Readme file
└── .vscode/         # VS Code configuration
    ├── settings.json
    └── tasks.json
```

## 🔧 Development

- Edit `main.py` to modify game logic
- Add libraries to `libs/` folder
- Use the REPL task for interactive testing

## 📝 Notes

- Don't forget to create and activate venv
- Ensure the ESP32 is connected to the correct serial port (/dev/tty.usbserial-210)
- For troubleshooting, check the MicroPython documentation and ESP32 pinouts.

