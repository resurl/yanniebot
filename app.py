import discord
import os
import random
import asyncio
import loadconfig
from dotenv import load_dotenv
from discord.ext import commands

load_dotenv()

## just make an .env and put KEY=your_api_token

bot = commands.Bot(command_prefix='.')
token = os.getenv('KEY')
chatChannel = None

## module handles connections, events & initializes cogs

@bot.event
async def on_ready():
    print('bot ready')
    print(f'Bot name: {bot.user.name}')
    print(f'Discord version: {discord.__version__}')
    for cog in loadconfig.__cogs__:
        try:
            bot.load_extension(cog)
        except Exception as e:
            print(f'couldn\'t load {cog}, {e}')


@bot.event
async def on_voice_state_update(member, before, after):
    chatChannel = discord.utils.get(member.guild.channels, name="general")
    if (before.channel and not after.channel):
        if (random.randint(1, 5) > 3):
            await chatChannel.send(f'bye {member.mention}. . .')

# testing commands!
@bot.command(aliases=['hi,hello'])
async def hello(ctx):
    await ctx.send(f'hello {ctx.author.mention}')
    
bot.run(token)

# want to have music bot fully implemented first
    # queue, skip, stop, playlist support? soundcloud............
    # if command is .play <url> list, first display search results and allow users to pick
# then tea game