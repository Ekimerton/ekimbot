def wordle_to_char(input):
    input = input.replace('⬛', '0')
    input = input.replace('🟨', '1')
    input = input.replace('🟩', '2')
    base_3 = int(input, 3)
    return chr(base_3)
