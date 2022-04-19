import discord
import math
import random
import re
import numpy as np
import os
import bitdotio
import aiocron

DISCORD_TOKEN = os.environ.get('DISCORD_TOKEN')
BITIO_TOKEN = os.environ.get('BITIO_TOKEN')

client = discord.Client()
b = bitdotio.bitdotio(BITIO_TOKEN)


@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))


@aiocron.crontab('30 3 * * *')
async def wordle_winner_job():
    conn = b.get_connection()
    cur = conn.cursor()

    cur.execute(
        'SELECT max("wordle_number") from "Ekimerton/ekimbot"."wordle"')
    latest_wordle = cur.fetchone()[0]

    cur.execute(
        'SELECT count(user_id), avg(wordle_in), min(wordle_in) FROM "Ekimerton/ekimbot"."wordle" WHERE "wordle_number" = {latest_wordle}'.format(latest_wordle=latest_wordle))
    daily_stats = cur.fetchone()
    player_count = daily_stats[0]
    avg_wordle = round(daily_stats[1], 2)
    min_wordle = daily_stats[2]

    cur.execute(
        'SELECT DISTINCT user_id FROM "Ekimerton/ekimbot"."wordle" WHERE wordle_number = {latest_wordle} AND wordle_in = {min_wordle}'.format(latest_wordle=latest_wordle, min_wordle=min_wordle))
    latest_winners = cur.fetchall()
    winners = [winner[0] for winner in latest_winners]

    winner_text = "👑 Today's winner **in {min_wordle}** for Wordle {latest_wordle}: \n".format(
        latest_wordle=latest_wordle, min_wordle=min_wordle)
    for winner in winners:
        user = await client.fetch_user(winner)
        winner_text += user.mention + ', '
    winner_text = winner_text[:-2]
    winner_text += "\n\n{player_count} players got today's Wordle within an average of {avg_wordle} tries.".format(
        player_count=player_count, avg_wordle=avg_wordle)
    general = client.guilds[0].text_channels[0]
    await general.send(winner_text)


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    banned_words = ['league of legends', 'league',
                    'ieague', 'dota', 'dota 2', 'aram', 'tft']
    regex = re.compile('|'.join(map(re.escape, banned_words)), re.IGNORECASE)
    if any(word in message.content.lower() for word in banned_words):
        await message.channel.send(":warning: Fatwa placed on " + message.author.mention + " for the following message :warning: : \n\n" + regex.sub("`REDACTED`", message.content) + '\n')
        await message.delete()

    if len(message.content) > 200:
        await message.channel.send(message.content)
        return

    if message.content.startswith('$coinflip'):
        rand = random.randint(0, 1)
        await message.channel.send("Heads" if rand else "Tails")

    if message.content.startswith('$team'):
        team_size = -1
        total_size = -1

        try:
            args = message.content.split(" ")
            team_size = int(args[1])
        except Exception as e:
            await message.channel.send(e)
            return

        users = []
        try:
            voice_channel = message.author.voice.channel
            for member in voice_channel.voice_states:
                user = await client.fetch_user(member)
                users.append(user.name)
            if 'Groovy' in users:
                users.remove('Groovy')
            total_size = len(users)
        except Exception as e:
            await message.channel.send(e)
            return

        perm = np.random.permutation(users)
        teams = np.array_split(perm, math.ceil(total_size / team_size))

        result = []
        for team in teams:
            team = [str(i) for i in team]
            result.append('(' + ', '.join(team) + ')')

        await message.channel.send(', '.join(result))

    if message.content.startswith('$wordleboard'):
        conn = b.get_connection()
        cur = conn.cursor()

        cur.execute('''
            SELECT user_id, count(wordle_number) as win_count FROM (
                SELECT DISTINCT user_id, wordle_number FROM "Ekimerton/ekimbot"."wordle" as w1
                WHERE wordle_in = (
                    SELECT min(wordle_in) FROM "Ekimerton/ekimbot"."wordle" as w2
                    WHERE w2.wordle_number = w1.wordle_number
                ) AND wordle_number > 300 AND hard_mode = true
            ) as w3
            GROUP BY w3.user_id
            ORDER BY win_count DESC LIMIT 3
        ''')
        top_winners = cur.fetchall()
        for i in range(len(top_winners)):
            top_winner_user = await client.fetch_user(top_winners[i][0])
            top_winner_mention = top_winner_user.mention
            top_winners[i] = (top_winner_mention, top_winners[i][1])

        top_winners.append(("Null", 0))

        cur.execute('''
            SELECT user_id, avg(best_in) as avg_in FROM (
                SELECT user_id, wordle_number, min(wordle_in) as best_in FROM "Ekimerton/ekimbot"."wordle"
                WHERE wordle_number > 300 AND hard_mode = true
                GROUP BY user_id, wordle_number) as w1
            GROUP BY w1.user_id
            ORDER BY avg_in LIMIT 3
        ''')
        top_averages = cur.fetchall()
        for i in range(len(top_averages)):
            top_average_user = await client.fetch_user(top_averages[i][0])
            top_average_mention = top_average_user.mention
            top_averages[i] = (top_average_mention,
                               round(top_averages[i][1], 2))

        leaderboard_text = '''
**🏆 Top 3 Wordle Winners:** \n
    🥇 {top_winners[0][0]} - {top_winners[0][1]}\n
    🥈 {top_winners[1][0]} - {top_winners[1][1]}\n
    🥉 {top_winners[2][0]} - {top_winners[2][1]}\n
**🏆 Top 3 Wordle Averages:** \n
    🥇 {top_averages[0][0]} - {top_averages[0][1]}\n
    🥈 {top_averages[1][0]} - {top_averages[1][1]}\n
    🥉 {top_averages[2][0]} - {top_averages[2][1]}\n
'''.format(top_winners=top_winners, top_averages=top_averages)

        await message.channel.send(leaderboard_text)

    if message.content.startswith('Wordle'):
        user_id = message.author.id
        wordle_number = message.content.split(" ")[1]
        wordle_in = message.content.split(" ")[2][0]
        hard_mode = message.content.split(" ")[2][3] == '*'

        conn = b.get_connection()
        cur = conn.cursor()
        try:
            cur.execute('INSERT INTO "Ekimerton/ekimbot"."wordle" ("user_id", "wordle_number", "wordle_in", "hard_mode") VALUES ({user_id}, {wordle_number}, {wordle_in}, {hard_mode})'.format(
                user_id=user_id, wordle_number=wordle_number, wordle_in=wordle_in, hard_mode=hard_mode))
            await message.add_reaction('✅')
        except:
            await message.add_reaction('❌')

client.run(DISCORD_TOKEN)
