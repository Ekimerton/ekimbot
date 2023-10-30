import discord
import os
from commands import coinflip, team

# Initialize Intents
intents = discord.Intents.default()
intents.message_content = True

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

client.run(DISCORD_TOKEN)
