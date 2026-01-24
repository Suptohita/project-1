from games import game1, game2
from libs import button
from time import sleep_ms

restart_btn = button.Button(12, debounce_ms=100)  # LEFT → Restart

while True:
    # Start Game 1
    game1.start_game()

    # After Game 1 Continue, move to Game 2
    game2.start_game()

    # Check global restart
    while True:
        if restart_btn.was_pressed():
            print("\nRestarting all games...\n")
            sleep_ms(500)
            break
        sleep_ms(50)
