# -*- coding: utf-8 -*-
"""
Created on Fri Dec 15 17:19:46 2023

@author: Jenna Poliansky
"""
# import tkinter as tk
import string
import socket
import sys
# Create and bind a socket to other player's computer
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
PORT = 1234
s.bind(('', PORT))  # Change to '0.0.0.0'- to connect to another computer
s.listen(3000)
cs, addr = s.accept()

# Variables
# A list containing all the hangman drawings
hangman = ["\n+--+\n   |\n   |\n   |\n  ===",
           "\n\+--+\n O  |\n    |\n    |\n ===",
           "\n\+--+\n O  |\n |  |\n    |\n ===",
           "\n\+--+\n O  |\n/|  |\n    |\n ===",
           "\n\+--+\n O  |\n/|\ |\n    |\n ===",
           "\n\+--+\n O  |\n/|\ |\n/   |\n ===",
           "\n\+--+\n O  |\n/|\ |\n/ \ |\n ==="]
# Round counter
round_counter = 1

# The word being given for the other player to guess
word = ''

# Counts the number of letters in word
counter = 0

# Keeps the correct letters guessed by other player in a list
correct_letters = []

# Keeps track of the wrong letters guessed by other player in a list
wrong_letters = []

# Indicates whether the player is guessing the word or choosing it
guessing = True

# Number of incorrect guesses allowed for the other player
guesses = 6

# Number of times other player has won guessing a word
win_guesses = 0

# Lives
lives = 6

# Score counter
score = 0

# Enemy score counter
enemy_score = 0

# Draw the hangman

# Calculate the correct number of dashes after each letter guess


def calculate_dashes(correct_letters):
    dashes = ''
    if (msg not in correct_letters):
        correct_letters.append(msg)
    for x in word:
        if (x in correct_letters):
            dashes += x + ' '
        else:
            dashes += '_ '
    return dashes

# End the game once rounds finish


def round_update(round_counter, score, enemy_score):
    if (round_counter > 10):
        print("Game over! The final score is: ")
        print('You:', score, '-', 'Player 1:', enemy_score, '\n')
        if (score > enemy_score):
            print("You win!")
        elif (score == enemy_score):
            print("It's a tie!")
        else:
            print("You lose.")
        sys.exit()
    else:
        print('You:', score, '-', 'Player 1:', enemy_score, '\n')
        print('Round:', round_counter, '\n')

# Reformat the wrong letters to be shown


def wrong_letters_update(wrong_letters):
    if (msg not in word):
        wrong_letters.append(msg)
    wrong_letters_string = ''
    for x in wrong_letters:

        if (len(wrong_letters) == 1):
            wrong_letters_string = x
        else:
            wrong_letters_string += x + ', '
    return wrong_letters_string


# Instructions
print("Welcome to Co-Op Hangman! You and one other player will play 10 rounds, where each round the roles will switch.\n")
print("The guesser will have a limited number of guesses each round. Should they win a round, they will gain an additional guess for their next guessing round.\n")
print("The winner of each round gains a point. At the end of the 10 rounds, the winner is the one with the most points.\n")
print("Good luck!\n")

# Print the round number
print('Round:', round_counter, '\n')

while True:
    # Print role details when roles switch
    if (guessing == True):
        print("You are now guessing the word!\n")
        print("Lives: " + str(lives)+'\n')
    else:
        print("You are now choosing the word!\n")

    # Guessing the other player's word
    while (guessing == True):
        # Player 2 (server) recieves Player 1's (client) messages
        recv_message = cs.recv(4096)
        decoded_msg = recv_message.decode('utf-8')
        print('Player 1: ', recv_message.decode('utf-8'))

        # If player has guessed the word, increase the score, update the round and change roles
        if ('You win!' in decoded_msg):
            score = score + 1
            round_counter += 1
            lives += 1
            round_update(round_counter, score, enemy_score)
            guessing = False
            break
        # Else if player did not manage to guess the word, update the round and change roles
        elif (':(' in decoded_msg):
            round_counter += 1
            enemy_score += 1
            round_update(round_counter, score, enemy_score)
            guessing = False
        else:
            # Ensure guesses are valid: single letters a-z
            valid_message = False
            while not valid_message:
                message = input("You: ")
                # Account for wrong data types
                if not isinstance(message, str):
                    print("Please enter a string\n")

                # Account for incorrect lengths
                elif len(message) != 1:
                    print("Please enter a single letter\n")

                # Account for already guessed letters
                elif message in correct_letters or message in wrong_letters:
                    print("You have already guessed this letter.\n")

                # Account for incorrect string types
                elif message.lower() not in string.ascii_lowercase:
                    print("Please enter a letter between a-z\n")

                else:
                    # Send guess to other player
                    cs.send(bytes(message, 'utf-8'))
                    valid_message = True

    # Choosing a word for the other player
    while (guessing == False):
        # Choose a word and send the corresponding number of dashes
        if (word == ''):
            # Clear correct_letters and wrong_letters to reset them for a new round
            correct_letters.clear()
            wrong_letters.clear()

            # Create a string of dashes corresponding to the number of letters in the word
            word = input('You: ')
            word = word.lower()
            counter = len(word)
            dashes = '_ ' * len(word)
            # Create the hangman graphic
            hangman = ("\n+--+\n   |\n   |\n   |\n  ===")
            final_hangman = hangman+'        '+dashes

            # Send dahes and the hangman to server
            cs.send(bytes(final_hangman.encode("utf-8")))

        # Recieve letter guess from other player
        msg = cs.recv(1024).decode("utf-8")
        print('Player 1:', msg, '\n')
        msg = msg.lower()

        # Take proper actions if the letter is in the word
        if (msg in word):
            if (counter > 0):
                for x in word:
                    if (x == msg):
                        counter -= 1
                # If all letters have been guessed, send a win message, update scores and guessescounter-=1
                if (counter == 0):
                    win_message = 'You win! The word was: '+word+'\n'
                    correct_letters.clear()
                    wrong_letters.clear()
                    win_guesses += 1
                    guesses = 6+win_guesses
                    enemy_score += 1
                    round_counter += 1
                    round_update(round_counter, score, enemy_score)
                    cs.send(bytes(win_message.encode("utf-8")))

                    word = ''
                    guessing = True
                # Send a new set of dashes with the correct letter added in the right spot
                else:
                    correct_letter = msg+' is in the word\n' + hangman+'        ' + calculate_dashes(
                        correct_letters)+'   Wrong letters guessed: ' + wrong_letters_update(wrong_letters) + '\n'
                    cs.send(bytes(correct_letter.encode("utf-8")))

        # If the letter is not in the word, send a wrong letter message
        else:
            guesses -= 1
            wrong_letter = msg+' is not in the word\n'
            # Adjust hangman figure according to how many wrong letters have been guessed
            match guesses:
                case 11:
                    hangman = "\n+--+\n   |\n   |\n   |\n  ==="
                case 10:
                    hangman = "\n+--+\n   |\n   |\n   |\n  ==="
                case 9:
                    hangman = "\n+--+\n   |\n   |\n   |\n  ==="
                case 8:
                    hangman = "\n+--+\n   |\n   |\n   |\n  ==="
                case 7:
                    hangman = "\n+--+\n   |\n   |\n   |\n  ==="
                case 6:
                    hangman = "\n+--+\n   |\n   |\n   |\n  ==="
                case 5:
                    hangman = "\n\+--+\n O  |\n    |\n    |\n ==="
                case 4:
                    hangman = "\n\+--+\n O  |\n |  |\n    |\n ==="
                case 3:
                    hangman = "\n\+--+\n O  |\n/|  |\n    |\n ==="
                case 2:
                    hangman = "\n\+--+\n O  |\n/|\ |\n    |\n ==="
                case 1:
                    hangman = "\n\+--+\n O  |\n/|\ |\n/   |\n ==="
                case 0:
                    hangman = "\n\+--+\n O  |\n/|\ |\n/ \ |\n ==="
                    wrong_letter = msg + \
                        ' is not in the word\n\nYou have run out of guesses :(\n The word was: ' + \
                        word+'\n'
                    score = score + 1
                    round_counter += 1

            # Send the combined graphic
            final_hangman = wrong_letter+hangman + '        ' + \
                calculate_dashes(correct_letters)+'Wrong letters: ' + \
                wrong_letters_update(wrong_letters)+'\n'
            cs.send(bytes(final_hangman.encode('utf-8')))
        # If there are no more guesses left for the other player, switch roles
        if (guesses == 0):
            word = ''
            guesses = 6+win_guesses
            round_update(round_counter, score, enemy_score)
            guessing = True


cs.close()
s.close()
