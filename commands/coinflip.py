import random
import discord


async def run_command(message: discord.Message):
    rand = random.randint(0, 1)
    await message.channel.send("Heads" if rand else "Tails")
