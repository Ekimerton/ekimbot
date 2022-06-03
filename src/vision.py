from queries import *
from utils import *
import re
import math

user_starters = get_user_starters(178334565146951680)
user_starters = [(num, char_to_wordle(starter))
                 for num, starter in user_starters]
prev_answers = get_wordle_answers()
wordle_bank = get_wordle_bank()

guess = ['.', '.', '.', '.', '.']

for num, starter in user_starters[1:]:
    answer = prev_answers[num]
    green_idxs = [i for i, ltr in enumerate(starter) if ltr == '2']
    for green_idx in green_idxs:
        if guess[green_idx] == '.':
            guess[green_idx] = answer[green_idx]
        elif guess[green_idx] != answer[green_idx]:
            break

regex = re.compile("".join(guess).lower())
filtered_list = list(filter(regex.match, wordle_bank))
print(guess)
max_broken = 0
max_broken_words = []

for word in filtered_list:
    broken = False
    for idx, user_starter in enumerate(user_starters[1:]):
        num, starter = user_starter
        evaluated = wordle_evaluate(word, prev_answers[num].lower())
        if evaluated != starter:
            if idx > max_broken:
                max_broken = idx
                max_broken_words = [word]
            elif idx == max_broken:
                max_broken_words.append(word)
            broken = True
            break
    if not broken:
        max_broken = math.inf
        if max_broken_words:
            max_broken_words = []
        max_broken_words.append(word)

print(max_broken_words)
