import discord
import asyncio
import youtube_dl
from discord.ext import commands

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
    async def list_from_url(cls, title, *, loop=None):
        string = f'Displaying results for {title}:\n```'
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(title, download=False))

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


class Music(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=['p,play'])
    async def play(self, ctx, url=None, showResults=None):
        if (url != None):
            channel = ctx.author.voice.channel
            await channel.connect()
            vc = ctx.voice_client

            async with ctx.typing():
                player = await YTDLSource.from_url(url, loop=self.bot.loop, stream=True)
                ctx.voice_client.play(player, after=lambda e: print('Player error: %s' % e) if e else None)
            
                await ctx.send(f'Now playing: {player.title}')
        else:
            if (ctx.voice_client.is_paused):
                ctx.voice_client.resume()
            ctx.send('No URL specified!')

    # if audio is playing
    @commands.command()
    async def pause(self, ctx):
        if (ctx.voice_client.is_playing):
            ctx.voice_client.pause()

    @commands.command()
    async def leave(self, ctx):
        await ctx.voice_client.disconnect()
        
def setup(bot):
    bot.add_cog(Music(bot))