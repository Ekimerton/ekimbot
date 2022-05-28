import numpy as np
import requests
from bs4 import BeautifulSoup


def wordle_to_char(wordle_input):
    wordle_input = wordle_input.replace('⬛', '0')
    wordle_input = wordle_input.replace('⬜', '0')
    wordle_input = wordle_input.replace('🟨', '1')
    wordle_input = wordle_input.replace('🟩', '2')
    base_3 = int(wordle_input, 3)
    return chr(base_3 + 20)


def char_to_wordle(char):
    num = ord(char) - 20
    base_3 = np.base_repr(num, base=3)
    formatted = base_3.zfill(5)
    return formatted


def get_wordle_data():
    url = "https://progameguides.com/wordle/all-wordle-answers-in-2022-updated-daily/"
    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')
    word_list = []
    for ul_tag in soup.find_all('ul'):
        for li_tag in ul_tag.find_all('li'):
            try:
                text = li_tag.text
                day_sym = text.index('#')
                day = int(text[day_sym + 1:day_sym + 4])
                word = text[day_sym + 6:]
                word_list.append((day, word))
            except:
                pass
    return word_list
