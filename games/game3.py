from machine import Pin
from libs import rgb_led, button, pot_dimmer
from math import sqrt, floor
from time import sleep_ms, ticks_ms, ticks_diff


def start_game(player_num=1):
    restart_btn = button.Button(12, debounce_ms=100)
    lock_btn = button.Button(4, debounce_ms=100)
    hint_btn = button.Button(16, debounce_ms=100)

    rgb = rgb_led.RGBLED(15, 2, 17)
    dimmer_map = {
        "R": pot_dimmer.PotDimmer(32, 15),
        "G": pot_dimmer.PotDimmer(33, 2),
        "B": pot_dimmer.PotDimmer(35, 17)
    }

    # Predefined sequence of 10 colors with names
    color_sequence = [
        ("Red", (255, 0, 0)),
        ("Orange", (255, 128, 0)),
        ("Yellow", (255, 255, 0)),
        ("Yellow-Green", (128, 255, 0)),
        ("Green", (0, 255, 0)),
        ("Cyan", (0, 255, 255)),
        ("Blue", (0, 0, 255)),
        ("Indigo", (75, 0, 130)),
        ("Purple", (128, 0, 255)),
        ("Magenta", (255, 0, 255))
    ]

    GAME_STATE = "START"
    current_color_index = 0
    score = 0
    time_limit_seconds = 60
    matched_colors = []
    last_printed_time = -1
    last_led_rgb = (0, 0, 0)  # Track last set color
    led_deadband = 5  # Only update if change > 5

    def normalize_pot_value(val):
        if val > 255:
            return int((val / 4095) * 255)
        return int(val)

    def calculate_score(target, current):
        tr, tg, tb = target
        cr, cg, cb = current
        error = sqrt((tr - cr) ** 2 + (tg - cg) ** 2 + (tb - cb) ** 2)
        max_error = 441.67
        return int(max(0, 100 - (error / max_error * 100)))

    def check_global_restart():
        nonlocal GAME_STATE, score, current_color_index, matched_colors
        if restart_btn.was_pressed():
            print("\n" * 5)
            print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
            print("!!!   GAME RESTARTING      !!!")
            print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
            sleep_ms(500)
            GAME_STATE = "START"
            score = 0
            current_color_index = 0
            matched_colors = []

    def print_separator():
        print("\n" + "-" * 50)

    def print_header(title):
        print("\n" + "=" * 50)
        print(title.center(50))
        print("=" * 50)

    def format_time(seconds):
        mins = seconds // 60
        secs = seconds % 60
        return f"{mins:02d}:{secs:02d}"

    def print_color_list(time_remaining, current_target_name):
        print_header("COLOR LIST - MATCH IN ORDER")
        print(f"Time remaining: {format_time(time_remaining)}")
        print_separator()
        for i, (name, _) in enumerate(color_sequence):
            if i in matched_colors:
                print(f"  ✓ {name}")
            elif i == current_color_index:
                print(f"  → {name} (CURRENT)")
            else:
                print(f"    {name}")
        print_separator()
        print(f"Current target: {current_target_name}")
        print("Mix this color using the RGB knobs!")
        print("LED shows YOUR mix (not the target)")

    def print_match_result(accuracy, success, color_name, total_score, colors_matched):
        print_separator()
        if success:
            print(f"MATCHED! {color_name}")
            print(f"Accuracy: {accuracy}%")
            print(f"Score: +10 points (Total: {total_score})")
            print(f"Colors completed: {colors_matched}/{len(color_sequence)}")
        else:
            print(f"Missed! Accuracy: {accuracy}% (Need ≥80%)")
            print(f"Keep trying to match: {color_name}")
        print_separator()

    def print_final_result(total_score, colors_matched, total_colors):
        print("\n" + "=" * 50)
        print("TIME'S UP!".center(50))
        print("=" * 50)
        print(f"Colors matched: {colors_matched}/{total_colors}")
        print(f"Total score: {total_score} points")
        print("=" * 50)
        print("\n[Press RIGHT button to continue]")

    print("\n\n")
    print("=" * 50)
    print("GAME 3: SEQUENTIAL COLOR CHALLENGE".center(50))
    print(f"PLAYER {player_num}".center(50))
    print("=" * 50)
    print("Match colors by name in sequence!")
    print("You have 1 minute to match as many as possible.")
    print("Each successful match (≥80% accuracy) = +10 points")
    print("You must match colors in order - can't skip ahead!")
    print("LED shows YOUR mix (not the target color)")
    print("-" * 50)
    print("Controls:")
    print("  • Turn RGB knobs to mix the target color")
    print("  • MIDDLE button = Lock in your answer")
    print("=" * 50)
    print("\nReady to start...")
    sleep_ms(2000)

    while True:
        check_global_restart()

        if GAME_STATE == "START":
            score = 0
            current_color_index = 0
            matched_colors = []
            game_start_time = ticks_ms()
            time_limit_ms = time_limit_seconds * 1000
            last_printed_time = -1
            GAME_STATE = "PLAYING"

            # Show initial color list
            current_color_name, target_rgb = color_sequence[current_color_index]
            print_color_list(time_limit_seconds, current_color_name)
            last_printed_time = time_limit_seconds

        elif GAME_STATE == "PLAYING":
            # Check time limit
            current_time = ticks_ms()
            elapsed = ticks_diff(current_time, game_start_time)
            time_remaining_ms = time_limit_ms - elapsed
            time_remaining_s = time_remaining_ms // 1000

            if time_remaining_ms <= 0:
                GAME_STATE = "END"
                continue

            # Check if we've completed all colors
            if current_color_index >= len(color_sequence):
                GAME_STATE = "END"
                continue

            # Get current target
            current_color_name, target_rgb = color_sequence[current_color_index]

            # Update current RGB from potentiometers
            r = normalize_pot_value(dimmer_map["R"].update())
            g = normalize_pot_value(dimmer_map["G"].update())
            b = normalize_pot_value(dimmer_map["B"].update())
            current_rgb = (r, g, b)

            # Only update LED if values changed significantly (deadband)
            if (abs(r - last_led_rgb[0]) > led_deadband or
                abs(g - last_led_rgb[1]) > led_deadband or
                    abs(b - last_led_rgb[2]) > led_deadband):
                rgb.set_color(*current_rgb)
                last_led_rgb = current_rgb

            # Periodically update timer display (every second)
            if time_remaining_s != last_printed_time and time_remaining_s > 0:
                print(
                    f"⏱ Time remaining: {format_time(time_remaining_s)}", end='\r')
                last_printed_time = time_remaining_s

            # Check if lock button pressed
            if lock_btn.was_pressed():
                # Evaluate current match
                accuracy = calculate_score(target_rgb, current_rgb)
                if accuracy >= 80:
                    score += 10
                    matched_colors.append(current_color_index)
                    print_match_result(
                        accuracy, True, current_color_name, score, len(matched_colors))

                    # Move to next color
                    current_color_index += 1

                    # Check if completed all colors
                    if current_color_index >= len(color_sequence):
                        sleep_ms(2000)
                        GAME_STATE = "END"
                        continue

                    # Show updated list with new current color
                    current_color_name, target_rgb = color_sequence[current_color_index]
                    current_time = ticks_ms()
                    elapsed = ticks_diff(current_time, game_start_time)
                    time_remaining_ms = time_limit_ms - elapsed
                    time_remaining_s = time_remaining_ms // 1000
                    print_color_list(time_remaining_s, current_color_name)
                    last_printed_time = time_remaining_s
                    sleep_ms(1000)
                else:
                    print_match_result(
                        accuracy, False, current_color_name, score, len(matched_colors))
                    sleep_ms(1000)

            sleep_ms(50)

        elif GAME_STATE == "END":
            rgb.set_color(0, 0, 0)  # Turn off LED
            print_final_result(score, len(matched_colors), len(color_sequence))
            while True:
                check_global_restart()
                if hint_btn.was_pressed():
                    print("\nContinuing...")
                    sleep_ms(500)
                    return score
                sleep_ms(50)
