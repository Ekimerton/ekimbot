def wordle_to_char(wordle_input):
    wordle_input = wordle_input.replace('⬛', '0')
    wordle_input = wordle_input.replace('🟨', '1')
    wordle_input = wordle_input.replace('🟩', '2')
    base_3 = int(wordle_input, 3)
    return chr(base_3 + 20)
