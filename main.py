import discord
import math
import random
import re
import numpy as np
import os
import bitdotio

DISCORD_TOKEN = os.environ.get('DISCORD_TOKEN')
BITIO_TOKEN = os.environ.get('BITIO_TOKEN')


client = discord.Client()
b = bitdotio.bitdotio(BITIO_TOKEN)


@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))


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

    if message.content.startswith('$help'):
        await message.channel.send(
            '''
            Use $team x to generate teams of x \n
            Use $coinflip to flip a coin
            '''
        )

    if message.content.startswith('$wordleboard'):
        conn = b.get_connection()
        cur = conn.cursor()

        cur.execute(
            'SELECT max("wordle_number") from "Ekimerton/ekimbot"."wordle"')
        latest_wordle = cur.fetchone()[0]

        cur.execute(
            'SELECT min(wordle_in) FROM "Ekimerton/ekimbot"."wordle" WHERE "wordle_number" = {latest_wordle}'.format(latest_wordle=latest_wordle))
        latest_best = cur.fetchone()[0]

        cur.execute(
            'SELECT DISTINCT user_id FROM "Ekimerton/ekimbot"."wordle" WHERE wordle_number = {latest_wordle} AND wordle_in = {latest_best}'.format(latest_wordle=latest_wordle, latest_best=latest_best))
        latest_winners = cur.fetchall()
        winners = [winner[0] for winner in latest_winners]

        winner_text = "Current winner(s) for wordle {latest_wordle} with a score of {latest_best}/6: \n\n".format(
            latest_wordle=latest_wordle, latest_best=latest_best)
        for winner in winners:
            user = await client.fetch_user(winner)
            winner_text += user.mention + '\n'
        await message.channel.send(winner_text)

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
