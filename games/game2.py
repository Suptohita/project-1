from machine import Pin
from libs import rgb_led, button, pot_dimmer
from math import sqrt
from time import sleep_ms


def start_game(player_num=1):
    restart_btn = button.Button(12, debounce_ms=100)  # LEFT → Restart
    lock_btn = button.Button(4, debounce_ms=100)   # MIDDLE → Lock In
    hint_btn = button.Button(16, debounce_ms=100)  # RIGHT → disabled in Game 2

    rgb = rgb_led.RGBLED(15, 2, 17)
    dimmer_map = {
        "R": pot_dimmer.PotDimmer(32, 15),
        "G": pot_dimmer.PotDimmer(33, 2),
        "B": pot_dimmer.PotDimmer(35, 17)
    }

    target_colors = [
        (255, 0, 0), (0, 255, 0), (0, 0, 255),
        (255, 255, 0), (0, 255, 255)
    ]

    current_round = 0
    score = 0

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
        nonlocal GAME_STATE, current_round, score
        if restart_btn.was_pressed():
            print("\n" * 5)
            print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
            print("!!!   GAME RESTARTING      !!!")
            print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
            sleep_ms(500)
            GAME_STATE = "START"
            current_round = 0
            score = 0

    def print_target_info(round_num, total):
        print("\n" + "=" * 50)
        print(f"COLOR SCAVENGER HUNT - P{player_num} ROUND {round_num}/{total}".center(50))
        print("=" * 50)
        print("Memorize the color shown on the LED")
        print("Adjust knobs to match, then press MIDDLE button to Lock In")
        print("Press LEFT button to Restart")
        print("=" * 50)

    def show_target_color(target, duration_ms=5000):
        rgb.set_color(*target)
        seconds = max(1, int(duration_ms / 1000))
        for remaining in range(seconds, 0, -1):
            print(f"Check the LED, turning off color in {remaining}")
            sleep_ms(1000)
        rgb.set_color(0, 0, 0)
        print("Time's up! Now guess the color.")

    def print_round_result(current_score):
        print(f"\nRound result: {current_score} points")
        print(f"Total score so far: {score}/{len(target_colors)}")
        print("=" * 50)

    def print_final_result():
        print("\n" + "=" * 50)
        print(f"GAME COMPLETE - P{player_num}".center(50))
        print(f"Your final score: {score}/{len(target_colors)}".center(50))
        print("=" * 50)
        print("\nPress RIGHT button to Continue or LEFT button to Restart")

    print(f"\nStarting Color Scavenger Hunt for Player {player_num}...")

    GAME_STATE = "START"

    while True:
        check_global_restart()

        if GAME_STATE == "START":
            current_round = 0
            score = 0
            print("Get ready for the first target...")
            sleep_ms(500)
            GAME_STATE = "ROUND"

        elif GAME_STATE == "ROUND":
            if current_round >= len(target_colors):
                GAME_STATE = "END"
                continue

            target = target_colors[current_round]
            print_target_info(current_round + 1, len(target_colors))
            show_target_color(target)

            round_done = False
            while not round_done:
                check_global_restart()
                if hint_btn.was_pressed():
                    print("\nHints are disabled in Game 2.")
                r = normalize_pot_value(dimmer_map["R"].update())
                g = normalize_pot_value(dimmer_map["G"].update())
                b = normalize_pot_value(dimmer_map["B"].update())
                current_rgb = (r, g, b)

                if lock_btn.was_pressed():
                    round_score = calculate_score(target, current_rgb)
                    if round_score >= 80:
                        score += 1
                        print_round_result(1)
                    else:
                        print_round_result(0)
                    current_round += 1
                    round_done = True

                sleep_ms(50)

        elif GAME_STATE == "END":
            print_final_result()
            while True:
                check_global_restart()
                if hint_btn.was_pressed():
                    print("\nContinuing...")
                    sleep_ms(500)
                    return score
                sleep_ms(50)
