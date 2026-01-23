from machine import I2C, Pin, SPI
import machine
from libs import rgb_led, button, pot_dimmer, ili9341
import time
from time import sleep_ms
from math import sqrt

# --- CONFIGURATION ---
BLACK = ili9341.color565(0, 0, 0)
WHITE = ili9341.color565(255, 255, 255)
BLUE  = ili9341.color565(0, 0, 255)
RED   = ili9341.color565(255, 0, 0)
GREEN = ili9341.color565(0, 255, 0)
YELLOW = ili9341.color565(255, 255, 0)

# Pins
TFT_CS = 5
TFT_DC = 21
TFT_RST = 22
spi = SPI(2, baudrate=40000000, polarity=0, phase=0, sck=Pin(18), mosi=Pin(23), miso=Pin(19))
display = ili9341.Display(spi, cs=Pin(TFT_CS), dc=Pin(TFT_DC), rst=Pin(TFT_RST), width=320, height=240, rotation=270)

# Inputs
lock_btn = button.Button(4, debounce_ms=100)
restart_btn = button.Button(12, debounce_ms=100)
hint_pin = Pin(16, Pin.IN, Pin.PULL_UP) 

rgb = rgb_led.RGBLED(15, 2, 17)
dimmer_map = {
    "R": pot_dimmer.PotDimmer(32, 15),
    "G": pot_dimmer.PotDimmer(33, 2),
    "B": pot_dimmer.PotDimmer(35, 17)
}

# --- HELPER FUNCTIONS ---

def check_global_restart():
    """Checks reset button and hard-resets the ESP32 if pressed."""
    if restart_btn.was_pressed():
        print("Restarting...")
        display.clear(BLACK)
        display.draw_text8x8(110, 110, "RESTARTING...", RED)
        sleep_ms(100)
        machine.reset()

def normalize_pot_value(val):
    if val > 255: return int((val / 4095) * 255)
    return int(val)

def calculate_score(target, current):
    tr, tg, tb = target
    cr, cg, cb = current
    # Max Euclidean distance (White to Black) is approx 441.67
    error = sqrt((tr - cr)**2 + (tg - cg)**2 + (tb - cb)**2)
    max_error = 441.67
    return int(max(0, 100 - (error / max_error * 100)))

# --- LAYOUT DRAWING FUNCTIONS ---

def draw_layout_default(target_rgb):
    """Layout A: Huge Target, No Mix Box."""
    display.clear(BLACK)
    display.draw_text8x8(10, 10, "TARGET COLOR", WHITE)
    t_color = ili9341.color565(*target_rgb)
    display.fill_rectangle(10, 25, 300, 185, t_color)
    display.draw_text8x8(10, 220, "Hold BTN 16 for Hint | Lock: BTN 4", WHITE)

def draw_layout_hint(target_rgb):
    """Layout B: Split Screen (Target Left, Mix Right)."""
    display.clear(BLACK)
    t_color = ili9341.color565(*target_rgb)
    
    # Left Side: Target
    display.draw_text8x8(10, 10, "TARGET", WHITE)
    display.fill_rectangle(10, 25, 140, 100, t_color)
    
    # Right Side: Mix
    display.draw_text8x8(170, 10, "YOUR MIX", WHITE)
    display.draw_rectangle(170, 25, 140, 100, WHITE)

# --- GAME LOOP ---

GAME_STATE = "START"
target_rgb = (0,0,0)
current_rgb = (0,0,0)
last_rgb = (-1,-1,-1)

is_hinting = False 
hint_count = 0 

print("System Ready.")

while True:
    check_global_restart()

    if GAME_STATE == "START":
        display.draw_text8x8(100, 110, 'Generating...', BLUE)
        sleep_ms(500)
        
        target_rgb = rgb.generate_random_color(True)
        print(f"Target: {target_rgb}")
        
        # Reset Game Variables
        hint_count = 0 
        is_hinting = False
        
        draw_layout_default(target_rgb)
        GAME_STATE = "MIXING"

    elif GAME_STATE == "MIXING":
        # 1. Update Hardware
        r = normalize_pot_value(dimmer_map["R"].update())
        g = normalize_pot_value(dimmer_map["G"].update())
        b = normalize_pot_value(dimmer_map["B"].update())
        current_rgb = (r, g, b)

        # 2. Check Hint Button (Active Low)
        button_pressed = (hint_pin.value() == 0)
        
        # TRANSITION: Released -> Pressed
        if button_pressed and not is_hinting:
            is_hinting = True
            hint_count += 1
            print(f"Hint used! Count: {hint_count}")
            draw_layout_hint(target_rgb)
            last_rgb = (-1,-1,-1)

        # TRANSITION: Pressed -> Released
        elif not button_pressed and is_hinting:
            is_hinting = False
            draw_layout_default(target_rgb)

        # 3. Dynamic Screen Updates
        if is_hinting:
            if abs(r - last_rgb[0]) > 2 or abs(g - last_rgb[1]) > 2 or abs(b - last_rgb[2]) > 2:
                mix_color = ili9341.color565(r, g, b)
                display.fill_rectangle(170, 25, 140, 100, mix_color)
                
                status = f"R:{r:03} G:{g:03} B:{b:03}"
                display.draw_text8x8(80, 160, status, WHITE)
                last_rgb = current_rgb

        # 4. Check Lock
        if lock_btn.was_pressed():
            GAME_STATE = "RESULT"

    elif GAME_STATE == "RESULT":
        # --- CALCULATE SCORES ---
        
        # 1. Raw Accuracy (0-100%)
        raw_accuracy = calculate_score(target_rgb, current_rgb)
        
        # 2. Penalty Calculation
        penalty_percentage = hint_count * 5
        if penalty_percentage > 100: penalty_percentage = 100
        
        # 3. Final Total Score (Integer)
        penalty_factor = (100 - penalty_percentage) / 100.0
        final_score = int(raw_accuracy * penalty_factor)
        
        # --- DRAW VISUALS ---
        display.clear(BLACK)
        
        # Target vs Mix
        t_color = ili9341.color565(*target_rgb)
        p_color = ili9341.color565(*current_rgb)
        
        display.draw_text8x8(10, 10, "TARGET", WHITE)
        display.fill_rectangle(10, 25, 140, 100, t_color)
        
        display.draw_text8x8(170, 10, "YOUR MIX", WHITE)
        display.fill_rectangle(170, 25, 140, 100, p_color)
        
        # --- DRAW DATA BREAKDOWN ---
        
        # Line 1: Match Accuracy
        display.draw_text8x8(10, 160, f"Match Accuracy: {raw_accuracy}%", WHITE)
        
        # Line 2: Hints & Penalty
        if hint_count > 0:
            penalty_msg = f"Hints: {hint_count} (Penalty: -{penalty_percentage}%)"
            display.draw_text8x8(10, 175, penalty_msg, YELLOW)
        else:
            display.draw_text8x8(10, 175, "Hints: 0 (Bonus: Clean Run)", GREEN)

        # Line 3: Final Score (Large & Colored)
        if final_score > 90:
            c = GREEN
            rank = "Excellent!"
        elif final_score > 70:
            c = BLUE
            rank = "Good Job"
        else:
            c = RED
            rank = "Try Again"

        # Note: No '%' symbol here, just the points
        display.draw_text8x8(10, 195, f"TOTAL SCORE: {final_score}", c)
        display.draw_text8x8(180, 195, rank, c)
        
        display.draw_text8x8(10, 220, "Next: Press Hint | Rst: BTN 12", WHITE)
        
        # Wait for input
        while True:
            check_global_restart()
            if hint_pin.value() == 0:
                sleep_ms(200)
                GAME_STATE = "START"
                break
            sleep_ms(50)

    sleep_ms(20)