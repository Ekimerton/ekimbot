import discord
import math
import random
import re
import numpy as np
import os

client = discord.Client()


@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    banned_words = ['league of legends', 'league', 'dota', 'dota 2']
    regex = re.compile('|'.join(map(re.escape, banned_words)), re.IGNORECASE)
    if any(word in message.content.lower() for word in banned_words):
        await message.channel.send(":warning: Fatwa placed on " + message.author.mention() + " for the following message :warning: : \n\n" + regex.sub("`REDACTED`", message.content) + '\n')
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
            author = message.author
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

discord_token = os.environ.get('DISCORD_TOKEN')
client.run(discord_token)
