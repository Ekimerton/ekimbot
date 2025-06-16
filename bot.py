import discord
import os
from commands import coinflip, team, ban, llm

# Initialize Intents
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

DISCORD_TOKEN = os.environ.get('DISCORD_TOKEN')
client = discord.Client(intents=intents)


@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('$coinflip'):
        await coinflip.run_command(message)
        return

    if message.content.startswith('$team'):
        await team.run_command(message)
        return

    if message.content.startswith('$ban'):
        await ban.run_command(message)
    
    if client.user in message.mentions:
        last_messages = []
        async for msg in message.channel.history(limit=3):
            last_messages.append(msg)
        await llm.run_command(message, last_messages)

    if message.content.startswith('$help'):
        help_message = """
Here are the commands you can use:

$coinflip - Flips a coin and returns either heads or tails.

$team [TEAM_SIZE] - Randomly divides the people in your voice channel into teams of the specified size. You need to be in a voice channel to use this.

$ban - Randomly selects a member from the server (excluding bots) and sends their name as a chosen one.
"""
        await message.channel.send(help_message)


client.run(DISCORD_TOKEN)
