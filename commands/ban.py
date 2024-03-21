import random
import discord


async def run_command(message: discord.Message):
    try:
        members = message.guild.members
        # Exclude bots
        users = [member.name for member in members if not member.bot]
        if not users:
            await message.channel.send("No members found.")
            return

        # Choose a random user
        random_user = random.choice(users)

        # Send the chosen user's name
        await message.channel.send(f"{random_user} has been chosen.")
    except Exception as e:
        await message.channel.send("An error occurred while attempting to select a random member.")
