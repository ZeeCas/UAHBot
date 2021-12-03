import os
import discord
from discord.ext import commands
import re
import requests
import random
import youtube_dl
import asyncio
from datetime import datetime
from dotenv import load_dotenv
load_dotenv()
import json


intents = discord.Intents.all()

bot = commands.Bot(command_prefix=',', intents=intents)

youtube_dl.utils.bug_reports_message = lambda: ''


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
    'source_address': '0.0.0.0' 
}

ffmpeg_options = {
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
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))

        if 'entries' in data:
            # take first item from a playlist
            data = data['entries'][0]

        filename = data['url'] if stream else ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)

class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.queue = {}
    @commands.command(pass_context=True)
    async def join(self, ctx):
        """Joins the bot to your current channel"""
        if not ctx.message.author.voice:
            await ctx.send('You must be connected to a voice channel.')
            return
        else:
            VC = ctx.author.voice.channel
            client = await VC.connect()

            await ctx.send(f'Connected to ``{VC}``')
            
    @commands.command(pass_context=True)
    async def leave(self, ctx):
        """Removes the bot from your current voice channel"""
        await ctx.voice_client.disconnect()
        
    @commands.command()
    async def plyt(self, ctx, link: str):
        """Plays a youtube video by url (predownloads)"""
        async with ctx.typing():
            player = await YTDLSource.from_url(link, loop=self.bot.loop)
            ctx.voice_client.play(player, after=lambda e: print('Player error: %s' % e) if e else None)
        await ctx.send('Now playing: {}'.format(player.title))
        
    @commands.command()
    async def stream(self, ctx, link: str):
        """Plays a youtube video by url (streams)"""
        try:
            if "http" in link or "www." in link:
                async with ctx.typing():
                    song_info = ytdl.extract_info(link, download=False)
                    with open("song_info.log","w") as log:
                        log.write(str(song_info))
                    #ctx.voice_client.play(discord.FFmpegPCMAudio(song_info["formats"][0]["url"]))

                    player = discord.FFmpegPCMAudio(song_info["formats"][0]["url"])
                    title = song_info["title"]
                    #print(song_info["formats"][0]["url"])

                    
                    if len(self.queue) == 0:
                        self.startPlaying(ctx.voice_client, player)
                        await ctx.send('Now playing: {}'.format(title))
                        
                    else:
                        self.queue[len(self.queue)] = player
                        await ctx.send('Added to queue: {}'.format(title))
            else: 
                link = str(link).replace(" ","+")
                html = requests.get(f"https://www.youtube.com/results?search_query={title}")
                video_ids = re.findall(r"watch\?v=(\S{11})", html.content.decode())
                async with ctx.typing():
                    player = await YTDLSource.from_url(video_ids[0], loop=self.bot.loop, stream = True)
                
                    if len(self.queue) == 0:
                        self.startPlaying(ctx.voice_client, player)
                        await ctx.send('Now playing: {}'.format(player.title))
                        
                    else:
                        self.queue[len(self.queue)] = player
                        await ctx.send('Added to queue: {}'.format(player.title))
        except Exception as e:
            print(e)
            await ctx.send(e)
                    
    def startPlaying(self, voice_client, player):
        
        self.queue[0] = player
        
        i = 0
        while i < len(self.queue):
            try:
                voice_client.play(self.queue[i], after=lambda e: print('Player error: %s' % e) if e else None)
                
            except:
                pass
            
            i+=1
             
    @commands.command()
    async def volume(self, ctx, volume: int):
        """Changes the volume"""
        ctx.voice_client.source.volume = volume / 100
        await ctx.send("Changed volume to {}%".format(volume))
        
    @commands.command()
    async def pause(self, ctx):
        """Pauses the audio coming the bot"""
        await ctx.voice_client.pause()
        
    @commands.command()
    async def resume(self, ctx):
        """Resumes the paused music"""
        await ctx.voice_client.resume()
        
    @commands.command()
    async def stop(self, ctx):
        """Removes the music from playing"""
        await ctx.voice_client.stop()
        
    @commands.command()
    async def yt(self, ctx, *title: str):
        """Searches for a youtube link by title, returns first result"""
        title = str(title).replace(" ","+")
        html = requests.get(f"https://www.youtube.com/results?search_query={title}")
        video_ids = re.findall(r"watch\?v=(\S{11})", html.content.decode())
        await ctx.send(f"https://www.youtube.com/watch?v={video_ids[0]}")

class Images(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    @commands.command()
    async def cat(self, ctx):
        """Returns an image of a O'Malley"""
        await ctx.send(file=discord.File(f"photos/{random.randrange(1,10)}.jpg"))

    @commands.command()
    async def duck(self, ctx):
        """Returns an image of a duck"""
        api = "https://random-d.uk/api/v2/random"
        data = requests.get(api)
        data = data.json()
        await ctx.send(data['url'])

    @commands.command()
    async def fox(self, ctx):
        """Returns an image of a fox"""
        api = "https://some-random-api.ml/img/fox"
        data = requests.get(api)
        data = data.json()
        await ctx.send(data['link'])

    @commands.command()
    async def whale(self, ctx):
        """Returns an image of a whale"""
        api = "https://some-random-api.ml/img/whale"
        data = requests.get(api)
        data = data.json()
        await ctx.send(data['link'])

    @commands.command()
    async def bird(self, ctx):
        """Returns an image of a bird"""
        api = "https://some-random-api.ml/img/birb"
        data = requests.get(api)
        data = data.json()
        await ctx.send(data['link'])

class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='8ball')
    async def _8ball(self, ctx):
        """Rolls an 8ball for you"""
        responses = ["No","Mayhaps","Ask again later","Are you dumb? Absolutely not.","Of course silly!","Its a little foggy","It's certain","Huh? I didn't catch that","Never. Not in a million years","I don't see why not?","That just isn't gonna work."]
        await ctx.send(random.choice(responses))

    @commands.command()
    async def quote(self, ctx):
        """Returns a quote from the list of quotes"""
        with open("./quotes","r") as quotes:
            lines = quotes.read().splitlines()
            await ctx.send(random.choice(lines))

    @commands.command()
    async def dance(self, ctx):
        """The bot does a little dance"""
        await ctx.send("ᕕ(⌐■_■)ᕗ ♪♬")

    @commands.command()
    async def coc(self, ctx):
        """Returns a random clash of clans guide"""
        listoguide = ["https://clashofclans.fandom.com/wiki/Flammy%27s_Strategy_Guides","https://medium.com/mr-ways-guide-to-clash-of-clans/clash-of-clans-the-ultimate-beginners-guide-830f6d7e0a74","https://houseofclashers.com/wiki/en/clash-of-clans-builder-base/strategy-guide/beginners-guide/"]
        await ctx.send(random.choice(listoguide))

    @commands.command()
    async def hw(self, ctx, target: str):
        """Tells someone to do their homework"""
        await ctx.send(f"Do your homework {target}!")
        await ctx.message.delete()

    @commands.command()
    async def wednesday(self, ctx):
        """Checks whether it is wednesday or not"""
        if (datetime.today().weekday() == 2):
            await ctx.send("It's wednesday my dudes")
            await ctx.message.delete()
        else:
            await ctx.send("It is not a wednesday <:sadge:906740836404981790>")
            await ctx.message.delete()

class Utility(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command()
    async def say(self, ctx, *message: str):
        """Parrots back what you say"""
        await ctx.send(" ".join(message))
        await ctx.message.delete()

    @commands.command()
    async def poll(self, ctx, *message: str):
        """Adds a poll to your message"""
        await ctx.message.add_reaction("✅")
        await ctx.message.add_reaction("🚫")
    # def reportAuthor(ctx)



bot.add_cog(Music(bot))
bot.add_cog(Images(bot))
bot.add_cog(Fun(bot))
bot.add_cog(Utility(bot))
print("Looks like we're online :)")
bot.run(os.getenv('DISCORD-TOKEN'))
