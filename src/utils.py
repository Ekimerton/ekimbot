import templates


def wordle_to_char(input):
    input = input.replace('⬛', '0')
    input = input.replace('🟨', '1')
    input = input.replace('🟩', '2')
    base_3 = int(input, 3)
    return chr(base_3)


print(wordle_to_char('⬛⬛⬛⬛⬛'))
print(templates.DAILY_WINNER.format(min_attempt='2', latest_wordle='100',
      winners='Ekim, Adam', player_count='5', avg_attempt='3.5'))
