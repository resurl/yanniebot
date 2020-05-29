import discord
import os
import youtube_dl
import random
import asyncio
from dotenv import load_dotenv
from discord.ext import commands

load_dotenv()

bot = commands.Bot(command_prefix='.')
token = os.getenv('KEY')
chatChannel = None

ytdl_format_options = {
    'format': 'bestaudio/best',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0' # bind to ipv4 since ipv6 addresses cause issues sometimes
}

ffmpeg_options = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 
    'options': '-vn'
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)

class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)
        self.data = data
        self.title = data.get('title')
        self.url = data.get('url')

    @classmethod
    async def list_from_url(cls, url, *, loop=None):
        string = f'Displaying results for {url}:\n```'
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=False))

        if 'entries' in data:
            for entry in data['entries']:
                string += entry.get('title')
        else:
            string += 'No entries found'
        string += "```"
        return string 

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))
        
        if 'entries' in data:
            data = data['entries'][0]

        filename = data['url'] if stream else ytdl.prepare_filename()
        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)


@bot.event
async def on_ready():
    print('bot ready')
    chatChannel = await bot.fetch_channel('479512513378123798')

@bot.event
async def on_voice_state_update(member, before, after):
    if (before.channel and not after.channel):
        if (random.randint(1, 5) > 3):
            await chatChannel.send(f'bye {member.mention}. . .')

@bot.command(aliases=['hi,hello'])
async def hello(ctx):
    await ctx.send(f'hello {ctx.author.mention}')

@bot.command(aliases=['p,play'])
async def play(ctx, url=None, showResults=None):
    if (url != None):
        channel = ctx.author.voice.channel
        await channel.connect()
        vc = ctx.voice_client

        # if showResults is false, i.e. msg is not of form '.play <url> list'
        if (showResults == "list"):
            message = await YTDLSource.list_from_url(url, loop=bot.loop)
            await ctx.send(f'{message}')
        elif (showResults == None):
            async with ctx.typing():
                player = await YTDLSource.from_url(url, loop=bot.loop, stream=True)
                ctx.voice_client.play(player, after=lambda e: print('Player error: %s' % e) if e else None)
        
            await ctx.send(f'Now playing: {player.title}')
        else:
            await ctx.send('i have no idea what you want me to do')
    else:
        if (ctx.voice_client.is_paused):
            ctx.voice_client.resume()
        chatChannel.send('No URL specified!')

# if audio is playing
@bot.command()
async def pause(ctx):
    if (ctx.voice_client.is_playing):
        ctx.voice_client.pause()

@bot.command()
async def leave(ctx):
    await ctx.voice_client.disconnect()
    
bot.run(token)

# want to have music bot fully implemented first
    # queue, skip, stop, playlist support? soundcloud............
    # if command is .play <url> list, first display search results and allow users to pick
# then tea game