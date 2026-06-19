import random


word_list = ["python", "computer", "network", "security", "programming"]


def display_title():
    print("=" * 50)
    print("          WELCOME TO HANGMAN GAME")
    print("=" * 50)
    print("Guess the hidden word one letter at a time.")
    print("Maximum Incorrect Guesses Allowed: 6")
    print("=" * 50)


def play_game():
    secret_word = random.choice(word_list).lower()

    guessed_letters = []
    incorrect_guesses = 0
    max_attempts = 6

    hidden_word = ["_"] * len(secret_word)

    while incorrect_guesses < max_attempts and "_" in hidden_word:
        print("\n" + "-" * 50)
        print("Word:", " ".join(hidden_word))
        print("Guessed Letters:", " ".join(guessed_letters))
        print(f"Wrong Guesses: {incorrect_guesses}/{max_attempts}")
        print(f"Remaining Attempts: {max_attempts - incorrect_guesses}")
        print("-" * 50)

        guess = input("Enter a letter: ").strip().lower()

        if len(guess) != 1:
            print("Please enter only ONE letter.")
            continue

        if not guess.isalpha():
            print("Please enter an alphabet only.")
            continue

        if guess in guessed_letters:
            print("You already guessed this letter.")
            continue

        guessed_letters.append(guess)

        if guess in secret_word:
            for index, letter in enumerate(secret_word):
                if letter == guess:
                    hidden_word[index] = guess

            print("Correct Guess!")
        else:
            incorrect_guesses += 1
            print("Wrong Guess!")

    print("\n" + "=" * 50)

    if "_" not in hidden_word:
        print("Congratulations! You Won!")
        print("The word was:", secret_word)
    else:
        print("Game Over!")
        print("You used all attempts.")
        print("The correct word was:", secret_word)

    print("=" * 50)


def main():
    display_title()

    while True:
        play_game()

        choice = input("\nPlay Again? (Y/N): ").strip().lower()

        if choice == "y":
            continue
        elif choice == "n":
            print("\nThank you for playing!")
            break
        else:
            print("\nInvalid choice. Exiting game.")
            print("Thank you for playing!")
            break


main()