import discord
import os
import youtube_dl
import random
from dotenv import load_dotenv
from discord.ext import commands
load_dotenv()

bot = commands.Bot(command_prefix='.')
token = os.getenv('KEY')

@bot.event
async def on_ready():
    print('bot ready')

@bot.command(aliases=['hi,hello'])
async def hello(ctx):
    await ctx.send(f'hello {ctx.author.mention}')

@bot.event
async def on_voice_state_update(member,before,after):
    if (before.channel and not after.channel):
        if (random.randint(1, 10) > 6):
            chatChannel = await bot.fetch_channel('479512513378123798')
            await chatChannel.send(f'bye {member.mention}. . .')
    
bot.run(token)
