import discord
import math
import random
import numpy as np
import os
import bitdotio
import aiocron
from src.queries import *
import src.templates as templates

DISCORD_TOKEN = os.environ.get('DISCORD_TOKEN')
BITIO_TOKEN = os.environ.get('BITIO_TOKEN')

client = discord.Client()
b = bitdotio.bitdotio(BITIO_TOKEN)


@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))


@aiocron.crontab('30 3 * * *')
async def wordle_winner_job():
    latest_wordle = get_latest_wordle()
    player_count, avg_attempt, min_attempt, winners = get_wordle_stats(
        latest_wordle)
    winners_text = ''
    for winner in winners:
        user = await client.fetch_user(winner)
        winners_text += user.mention + ', '
    winners_text = winners_text[:-2]
    general = client.guilds[0].text_channels[0]
    await general.send(templates.DAILY_WINNER.format(min_attempt, latest_wordle, winners_text, player_count, avg_attempt))


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('$coinflip'):
        rand = random.randint(0, 1)
        await message.channel.send("Heads" if rand else "Tails")
        return

    if message.content.startswith('$team'):
        team_size = -1
        total_size = -1
        users = []
        try:
            args = message.content.split(" ")
            team_size = int(args[1])
            voice_channel = message.author.voice.channel
            for member in voice_channel.voice_states:
                user = await client.fetch_user(member)
                users.append(user.name)
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
        return

    if message.content.startswith('$wordlestat'):
        target_id = ""
        target_user = {}
        try:
            target_id = message.content.split(" ")[1]
            target_id = target_id[2:-1]
            target_user = await client.fetch_user(target_id)
        except:
            target_id = message.author.id
            target_user = message.author
        user_avg, user_days = get_user_averages_tries(target_id)
        user_wins = get_user_wins(target_id)
        if not user_avg or not user_days or not user_wins:
            await message.channel.send(templates.PLAYER_NOT_FOUND)
            return
        await message.channel.send(templates.PLAYER_STATS.format(target_user=target_user.mention, user_days=user_days, user_avg=user_avg, user_wins=user_wins))
        return

    if message.content.startswith('$wordleboard'):
        top_winners = get_alltime_winners()
        for i in range(len(top_winners)):
            top_winner_user = await client.fetch_user(top_winners[i][0])
            top_winner_mention = top_winner_user.mention
            top_winners[i] = (top_winner_mention, top_winners[i][1])
        top_winners.append(("Null", 0))
        top_averages = get_alltime_averages()
        for i in range(len(top_averages)):
            top_average_user = await client.fetch_user(top_averages[i][0])
            top_average_mention = top_average_user.mention
            top_averages[i] = (top_average_mention,
                               round(top_averages[i][1], 2))
        await message.channel.send(templates.LEADERBOARD.format(top_winners=top_winners, top_averages=top_averages))
        return

    if message.content.startswith('Wordle'):
        user_id = message.author.id
        wordle_number = message.content.split(" ")[1]
        wordle_in = message.content.split(" ")[2][0]
        hard_mode = message.content.split(" ")[2][3] == '*'
        # If person fails wordle give them a 7/6
        wordle_in = 7 if wordle_in == "X" else wordle_in
        try:
            add_wordle_attempt(user_id, wordle_number, wordle_in, hard_mode)
            await message.add_reaction('✅')
        except:
            await message.add_reaction('❌')
        return

client.run(DISCORD_TOKEN)
