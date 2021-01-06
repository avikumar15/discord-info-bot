import os

import discord
from discord.ext import commands

print(os.getcwd())
token = open("../token.txt", "r").read()
client = discord.Client()


@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')


@client.event
async def on_message(ctx):
    if "hi" in str(ctx.content.lower()):
        await ctx.channel.send('Hello!')


client.run(token)
