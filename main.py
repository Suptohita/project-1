from games import game1, game2, game3
from libs import button
from time import sleep_ms

restart_btn = button.Button(12, debounce_ms=100)  # LEFT → Restart

while True:
    print("\n\n")
    print("=" * 50)
    print("COLOR MIXING CHAMPIONSHIP".center(50))
    print("=" * 50)
    print("Two players will compete in three games:")
    print("  • Game 1: Spectral Light Mixer (2 rounds)")
    print("  • Game 2: Color Scavenger Hunt (5 rounds)")
    print("  • Game 3: Time Attack Mode (2 minutes)")
    print("\nHighest combined score wins!")
    print("=" * 50)
    sleep_ms(2000)
    
    totals = [0, 0]

    # Player 1
    print("\n\n" + "=" * 50)
    print("PLAYER 1'S TURN".center(50))
    print("=" * 50)
    sleep_ms(1500)
    totals[0] += game1.start_game(player_num=1)
    totals[0] += game2.start_game(player_num=1)
    totals[0] += game3.start_game(player_num=1)
    print("\n" + "=" * 50)
    print(f"PLAYER 1 FINAL SCORE: {totals[0]} points".center(50))
    print("=" * 50)
    sleep_ms(2000)

    # Player 2
    print("\n\n" + "=" * 50)
    print("PLAYER 2'S TURN".center(50))
    print("=" * 50)
    sleep_ms(1500)
    totals[1] += game1.start_game(player_num=2)
    totals[1] += game2.start_game(player_num=2)
    totals[1] += game3.start_game(player_num=2)
    print("\n" + "=" * 50)
    print(f"PLAYER 2 FINAL SCORE: {totals[1]} points".center(50))
    print("=" * 50)
    sleep_ms(2000)

    # Final Results
    print("\n\n")
    print("=" * 50)
    print("FINAL RESULTS".center(50))
    print("=" * 50)
    print(f"Player 1: {totals[0]} points")
    print(f"Player 2: {totals[1]} points")
    print("=" * 50)
    
    if totals[0] > totals[1]:
        print("\n🏆 PLAYER 1 WINS! 🏆".center(50))
    elif totals[1] > totals[0]:
        print("\n🏆 PLAYER 2 WINS! 🏆".center(50))
    else:
        print("\n🤝 IT'S A TIE! 🤝".center(50))
    
    print("=" * 50)
    print("\n[Press LEFT button to play again]")
    
    while True:
        if restart_btn.was_pressed():
            print("\n🔄 Restarting championship...\n")
            sleep_ms(1000)
            break
        sleep_ms(50)
