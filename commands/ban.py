import random
import discord


async def run_command(message: discord.Message):
    try:
        # Make sure your bot has the 'members' intent enabled to use this
        members = []
        async for member in message.guild.fetch_members(limit=None):
            if not member.bot:  # Exclude bots
                members.append(member.name)

        if not members:
            await message.channel.send("No members found.")
            return

        # Choose a random user
        random_user = random.choice(members)

        # Send the chosen user's name
        await message.channel.send(f"{random_user} has been chosen.")
    except Exception as e:
        await message.channel.send(e)
