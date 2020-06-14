import discord
from discord.ext import commands

types = {
    "longest" : {
        "title": "Longest Word Game",
        "desc": "To participate, react with ✔",
        "color": 0x85558a,
        "fields": [
            {
                "name": "How to play",
                "value": "When the game starts, it'll give you 3 letters. Find the longest word containing those 3 letters!"
            },
            {
                "name": "Settings",
                "value": "$time - defines the time allotted for rounds"
            }
        ]
    }
}

class Games(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.players = []
        self.playerState = []

    async def longest(self,ctx):
        # first send lobby message
        # whoever reacts is part of the game (each user added to list of players)
        # asks for the longest word containing a 3 letter combination
        # as bot updates timer, it keeps track of answers per user
        # at the end of the timer, bot evaluates answers and awards a point to a user
        lobby = await ctx.send(embed=self.lobbyEmbed("long"))
        await lobby.add_reaction("✅")
    
    def lobbyEmbed(self, type) -> discord.Embed:
        embed = discord.Embed.from_dict(types.get('longest'))
        return embed

    def initPlayerState(self):
        for player in self.players:
            self.playerState.append({
                "username": player.name,
                "score": 0,
                "answers": []
            })
   
    @commands.command()
    async def game(self, ctx, option):
        if option=='long':
            await self.longest(ctx)

def setup(bot):
    bot.add_cog(Games(bot))
