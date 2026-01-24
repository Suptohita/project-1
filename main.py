from games import game1, game2
from libs import button
from time import sleep_ms

restart_btn = button.Button(12, debounce_ms=100)  # LEFT → Restart

while True:
    totals = [0, 0]

    # Player 1
    totals[0] += game1.start_game(player_num=1)
    totals[0] += game2.start_game(player_num=1)
    print(f"\nPlayer 1 total score: {totals[0]}\n")

    # Player 2
    totals[1] += game1.start_game(player_num=2)
    totals[1] += game2.start_game(player_num=2)
    print(f"\nPlayer 2 total score: {totals[1]}\n")

    print(f"Final totals -> Player 1: {totals[0]} | Player 2: {totals[1]}")

    if totals[0] > totals[1]:
        print("Player 1 wins!")
    elif totals[1] > totals[0]:
        print("Player 2 wins!")
    else:
        print("It's a tie!")

    print("\nPress LEFT button to restart the full match.")
    while True:
        if restart_btn.was_pressed():
            print("\nRestarting all games...\n")
            sleep_ms(500)
            break
        sleep_ms(50)
