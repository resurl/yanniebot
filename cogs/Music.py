import discord
import asyncio
import youtube_dl
import requests
import aiohttp
import urllib.parse
from bs4 import BeautifulSoup
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

# class to handle music queries
class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)
        self.data = data
        self.title = data.get('title')
        self.url = data.get('url')

    @classmethod
    async def fetch(cls,url,client):
        async with client.get(url) as response:
            assert response.status == 200
            return await response.text()

    @classmethod
    async def search(cls,*args, limit=4):

        """Generates metadata from Youtube search pages
        :param args:  What the user wants to search
        :param limit: (optional) How many entries of video metadata you want
        :return: Dict containing video's title, creator, and url 
        """

        search_terms = ' '.join(args[0])
        query = urllib.parse.quote(search_terms)
        BASE_URL = "https://youtube.com"
        url = f"{BASE_URL}/results?search_query={query}&pbj=1"
        html = ''
        async with aiohttp.ClientSession() as client:
            html = await cls.fetch(url,client)
        parser = BeautifulSoup(html, 'lxml')
        results = []
        incr = 0

        for entry in parser.select('.yt-lockup-content'):
            if incr <= limit:
                video = entry.select_one('a.spf-link')
                channel = entry.select_one('.yt-lockup-byline').select_one('a').string
                if ((video is not None) and (video['href'].startswith('/watch'))):
                    metadata = {
                        'title': video.string,
                        'url': video['href'],
                        'by': channel
                    }
                    results.append(metadata)
                else:
                    print('not found')
            incr += 1

        return results

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        # will most likely always be false b/c of performance speed
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))
        
        if 'entries' in data:
            data = data['entries'][0]

        filename = data['url'] if stream else ytdl.prepare_filename()
        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)



# Cog for music commands 
class Music(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    async def playMusic(self, context, chnl, url):
        await chnl.connect()
        vc = context.voice_client
        
        async with context.typing():
            player = await YTDLSource.from_url(url, loop=self.bot.loop, stream=True)
            context.voice_client.play(player, after=lambda e: print('Player error: %s' % e) if e else None)
                
            await context.send(f'Now playing: {player.title}') # put embed here later

    @commands.command()
    async def list(self, ctx, *query):
        tt_string = ' '.join(query)
        list_result = await YTDLSource.search(query)
        msg = f'>>> Results for **{tt_string}**\n'
        for x in list_result:
             msg += f'**{x["title"]} by {x["by"]}**\n{x["url"]}\n\n'
        await ctx.send(msg) 

    @commands.command(aliases=['p'])
    async def play(self, ctx, *query):
        channel = ctx.author.voice.channel
        terms = query[len(query)-1]
        if (query[0].startswith('https://')):
            query = ' '.join(query)
            await self.playMusic(ctx,channel,query)

        elif (query):
            result = YTDLSource.search(query, limit=1)
            await self.playMusic(ctx, channel, result[0]['url'])

        elif (ctx.voice_client.is_paused):
            ctx.voice_client.resume()

        else:
            await ctx.send('No query specified!')
        
    # if audio is playing
    @commands.command(aliases=['stop'])
    async def pause(self, ctx):
        if (ctx.voice_client.is_playing):
            ctx.voice_client.pause()

    @commands.command()
    async def leave(self, ctx):
        await ctx.voice_client.disconnect()
        
def setup(bot):
    bot.add_cog(Music(bot))