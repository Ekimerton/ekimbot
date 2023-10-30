import math
import numpy as np
import discord


async def run_command(message: discord.Message):
    team_size = -1
    total_size = -1
    users = []
    try:
        args = message.content.split(" ")
        team_size = int(args[1])
        voice_channel = message.author.voice.channel
        for member in voice_channel.voice_states:
            user = await message.guild.fetch_member(member)
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
