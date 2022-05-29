from queries import *
from utils import *
import re
# 178985515721162752
# 204413802509369344
user_starters = get_user_starters(204413802509369344)
user_starters = [(num, char_to_wordle(starter))
                 for num, starter in user_starters]
prev_answers = get_wordle_answers()
wordle_bank = get_wordle_bank()

guess = ['.', '.', '.', '.', '.']

for num, starter in user_starters:
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

for word in filtered_list:
    broken = False
    for idx, user_starter in enumerate(user_starters):
        num, starter = user_starter
        evaluated = wordle_evaluate(word, prev_answers[num].lower())
        if evaluated != starter:
            print(idx)
            broken = True
            break
    if not broken:
        print(word)
