DAILY_WINNER = '''
👑 Today's winner || in {min_attempt} || for Wordle {latest_wordle}:
{winners_text}

{player_count} players got today's Wordle within an average of {avg_attempt} tries.
'''

LEADERBOARD = '''
**🏆 Top 3 Wordle Winners:**

    🥇 {top_winners[0][0]} - {top_winners[0][1]}
    🥈 {top_winners[1][0]} - {top_winners[1][1]}
    🥉 {top_winners[2][0]} - {top_winners[2][1]}

**🏆 Top 3 Wordle Averages:**

    🥇 {top_averages[0][0]} - {top_averages[0][1]}
    🥈 {top_averages[1][0]} - {top_averages[1][1]}
    🥉 {top_averages[2][0]} - {top_averages[2][1]}
'''

PLAYER_NOT_FOUND = 'No stats found for that user.'

PLAYER_STATS = '''
Stats for {target_user}:

    📅 Days Played: {user_days}
    📈 Wordle Average: {user_avg}
    🏆 Wordle Wins: {user_wins}
'''
