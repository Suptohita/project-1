from machine import Pin, SPI, reset
from libs import rgb_led, button, pot_dimmer
from math import sqrt, floor
from time import sleep_ms

def start_game(player_num=1):
    restart_btn = button.Button(12, debounce_ms=100)
    lock_btn    = button.Button(4, debounce_ms=100)
    hint_btn    = button.Button(16, debounce_ms=100)

    rgb = rgb_led.RGBLED(15, 2, 17)
    dimmer_map = {
        "R": pot_dimmer.PotDimmer(32, 15),
        "G": pot_dimmer.PotDimmer(33, 2),
        "B": pot_dimmer.PotDimmer(35, 17)
    }

    GAME_STATE = "START"
    target_rgb = (0, 0, 0)
    current_rgb = (0, 0, 0)
    hint_count = 0
    hint_button_prev = 1
    score_history = []
    round_index = 0
    rounds_total = 2
    total_score = 0

    def check_global_restart():
        nonlocal GAME_STATE, score_history
        if restart_btn.was_pressed():
            print("\n" * 5)
            print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
            print("!!!   SYSTEM RESTARTING    !!!")
            print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
            score_history.clear()
            sleep_ms(500)
            reset()

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

    def get_bar(value, width=15):
        fill = floor((value / 255) * width)
        bar = "#" * fill + "." * (width - fill)
        return f"[{bar}]"

    def print_separator():
        print("-" * 50)

    def print_header(title):
        print("\n" + "=" * 50)
        print(title.center(50))
        print("=" * 50)

    def print_target_dashboard(rgb_val, player_num, round_num, total_rounds):
        print_header(f"ROUND {round_num}/{total_rounds} - TARGET COLOR")
        print("Match this color using the RGB knobs:")
        print_separator()
        print("CHANNEL | LEVEL                | VALUE")
        print_separator()
        print(f" Red    | {get_bar(rgb_val[0], 20)} | {rgb_val[0]:03}")
        print(f" Green  | {get_bar(rgb_val[1], 20)} | {rgb_val[1]:03}")
        print(f" Blue   | {get_bar(rgb_val[2], 20)} | {rgb_val[2]:03}")
        print_separator()

    def print_hint_dashboard(hint_num, target, current):
        print_header(f"HINT #{hint_num} - COMPARISON")
        print("Compare your mix with the target:")
        print_separator()
        print("CHANNEL | TARGET              | YOUR MIX")
        print_separator()
        print(f" Red    | {get_bar(target[0], 15)} {target[0]:03} | {get_bar(current[0], 15)} {current[0]:03}")
        print(f" Green  | {get_bar(target[1], 15)} {target[1]:03} | {get_bar(current[1], 15)} {current[1]:03}")
        print(f" Blue   | {get_bar(target[2], 15)} {target[2]:03} | {get_bar(current[2], 15)} {current[2]:03}")
        print_separator()
        print(f"Penalty: -{hint_num * 5}% (each hint costs 5%)")

    def print_result_card(target, current, raw_score, penalty_pct, final_score, hint_count, player_num, round_num, total_rounds):
        score_history.append({"player": player_num, "round": round_num, "score": final_score, "hints": hint_count})

        print_header(f"ROUND {round_num}/{total_rounds} RESULTS")
        print("Your match vs Target:")
        print_separator()
        print("CHANNEL | TARGET | YOUR MIX")
        print_separator()
        for ch, t, c in zip(["Red  ", "Green", "Blue "], target, current):
            print(f" {ch} |  {t:03}   |  {c:03}")
        print_separator()
        print(f"Accuracy: {raw_score}%")
        if hint_count:
            print(f"Hint penalty: -{penalty_pct}% ({hint_count} hint{'s' if hint_count > 1 else ''})")
        else:
            print("Hint penalty: 0% (Perfect - no hints used!)")
        print_separator()
        print(f"ROUND SCORE: {final_score} points".center(50))
        print("=" * 50)

        if len(score_history) > 1:
            print_header("YOUR PROGRESS")
            for entry in score_history:
                print(f"  Round {entry['round']}: {entry['score']} points ({entry['hints']} hint{'s' if entry['hints'] > 1 else ''})")
            print("=" * 50)

        if round_num < total_rounds:
            print("\n[Press RIGHT button for next round]")
        else:
            print("\n[Press RIGHT button to continue]")

    def print_game_total(player_num, total_score, total_rounds):
        print_header(f"GAME 1 COMPLETE - PLAYER {player_num}")
        print(f"Rounds completed: {total_rounds}/2")
        print(f"Total score: {total_score} points")
        print("=" * 50)
        print("\nGreat job! Moving to Game 2...")
        print("[Press RIGHT button to continue]")

    print("\n\n")
    print("=" * 50)
    print("GAME 1: SPECTRAL LIGHT MIXER".center(50))
    print(f"PLAYER {player_num}".center(50))
    print("=" * 50)
    print("Match the target color using the RGB knobs!")
    print("You'll play 2 rounds.")
    print_separator()
    print("Controls:")
    print("  • Turn RGB knobs to match the target")
    print("  • RIGHT button = Hint (costs 5% per hint)")
    print("  • MIDDLE button = Lock in your answer")
    print("=" * 50)
    print("\nReady to start...")
    sleep_ms(1500)

    while True:
        check_global_restart()

        if GAME_STATE == "START":
            print(f"\n🎨 Generating target color for Round {round_index + 1}...")
            sleep_ms(1000)
            target_rgb = rgb.generate_random_color(True)
            hint_count = 0
            hint_button_prev = 1
            print_target_dashboard(target_rgb, player_num, round_index + 1, rounds_total)
            GAME_STATE = "MIXING"

        elif GAME_STATE == "MIXING":
            r = normalize_pot_value(dimmer_map["R"].update())
            g = normalize_pot_value(dimmer_map["G"].update())
            b = normalize_pot_value(dimmer_map["B"].update())
            current_rgb = (r, g, b)

            if hint_btn.was_pressed():
                hint_count += 1
                print_hint_dashboard(hint_count, target_rgb, current_rgb)

            if lock_btn.was_pressed():
                GAME_STATE = "RESULT"

        elif GAME_STATE == "RESULT":
            raw_accuracy = calculate_score(target_rgb, current_rgb)
            penalty_percentage = hint_count * 5
            if penalty_percentage > 100: penalty_percentage = 100
            final_score = int(raw_accuracy * (100 - penalty_percentage) / 100.0)
            total_score += final_score
            print_result_card(
                target_rgb,
                current_rgb,
                raw_accuracy,
                penalty_percentage,
                final_score,
                hint_count,
                player_num,
                round_index + 1,
                rounds_total
            )

            while True:
                check_global_restart()
                if hint_btn.was_pressed():
                    round_index += 1
                    if round_index >= rounds_total:
                        GAME_STATE = "GAME_COMPLETE"
                    else:
                        print("\n\n✨ Starting Round {}...".format(round_index + 1))
                        sleep_ms(1000)
                        GAME_STATE = "START"
                    break
                sleep_ms(50)
        elif GAME_STATE == "GAME_COMPLETE":
            print_game_total(player_num, total_score, rounds_total)
            while True:
                check_global_restart()
                if hint_btn.was_pressed():
                    print("\n\nContinuing to Game 2...")
                    sleep_ms(500)
                    return total_score
                sleep_ms(50)
