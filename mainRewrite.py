#TODO ping command, pings every 30 seconds

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
# import pysftp

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

# class FTP(commands.Cog):
#     def __init__(self,bot):
#         self.bot = bot
#     def parseFTP(self, ctx, file: str):
#         with pysftp.Connection('127.0.0.1', port=39870, username='pythonboi', password='Mijo2003', cnopts=cnopts) as sftp:
#             with sftp.cd('.'):
#                 files = ",".split(sftp.listdir())

class Listeners(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.Utility = Utility(self.bot)

    @bot.event
    async def on_message(message):
        if message.content.lower().startswith("im "):
            await message.channel.send(f"Hi {message.content[3:]} i'm Dad")
        elif message.content.lower().startswith("i'm ") or message.content.lower().startswith("i’m "):
            await message.channel.send(f"Hi{message.content[3:]} i'm Dad")
        await bot.process_commands(message)

class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.Utility = Utility(self.bot)
        self.queue = {}
        self.link = ""


    @commands.command(pass_context=True)
    async def join(self, ctx):
        """Joins the bot to your current channel"""
        if not ctx.message.author.voice:
            await ctx.send('You must be connected to a voice channel.')
            return
        else:
            VC = ctx.author.voice.channel
            client = await VC.connect()
            self.queue = {}
            await ctx.send(f'Connected to ``{VC}``')
        self.Utility.reportAuthor(ctx.command,ctx.author)
            
    @commands.command(pass_context=True)
    async def leave(self, ctx):
        """Removes the bot from your current voice channel"""
        await ctx.voice_client.disconnect()
        self.Utility.reportAuthor(ctx.command,ctx.author)
        
    @commands.command(name="stream")
    async def queue(self, ctx, *link):
        """Plays a youtube video by url (streams)"""
        try:
            if not "http" in link and not "www." in link:
                link = self.Utility.getYTURL(link)
            async with ctx.typing():
                song_info = ytdl.extract_info(link, download=False)
                player = discord.FFmpegPCMAudio(song_info["formats"][0]["url"])
                self.title = song_info["title"]
                try:
                    async with ctx.typing():
                            self.start_playing(ctx.voice_client, player)
                            await ctx.send(f"**Now Playing:** ``{self.title}``")
                except Exception as e:
                    print(e)
        except Exception as e:
            print(e)
            await ctx.send(e)             
        self.Utility.reportAuthor(ctx.command,ctx.author)
       
    @commands.command()
    async def volume(self, ctx, volume: int):
        """Changes the volume"""
        ctx.voice_client.source.volume = volume / 100
        await ctx.send("Changed volume to {}%".format(volume))
        self.Utility.reportAuthor(ctx.command,ctx.author)
        
    @commands.command()
    async def pause(self, ctx):
        """Pauses the audio coming the bot"""
        await ctx.voice_client.pause()
        self.Utility.reportAuthor(ctx.command,ctx.author)
        
    @commands.command()
    async def resume(self, ctx):
        """Resumes the paused music"""
        await ctx.voice_client.resume()
        self.Utility.reportAuthor(ctx.command,ctx.author)
        
    @commands.command()
    async def stop(self, ctx):
        """Removes the music from playing"""
        await ctx.voice_client.stop()
        self.Utility.reportAuthor(ctx.command,ctx.author)
        
    @commands.command(name="np")
    async def nowPlaying(self,ctx):
        await ctx.send(f"**Now Playing:** ``{self.title}``")

    @commands.command()
    async def yt(self, ctx, *title: str):
        """Searches for a youtube link by title, returns first result"""
        title = str(title).replace(" ","+")
        html = requests.get(f"https://www.youtube.com/results?search_query={title}")
        video_ids = re.findall(r"watch\?v=(\S{11})", html.content.decode())
        await ctx.send(f"https://www.youtube.com/watch?v={video_ids[0]}")
        self.Utility.reportAuthor(ctx.command,ctx.author)
    
    def start_playing(self, voice_client, player):
        voice_client.play(player, after=lambda e: print('Done') if not e else None)

class Images(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.Utility = Utility(self.bot)
    @commands.command()
    async def cat(self, ctx):
        """Returns an image of a O'Malley"""
        await ctx.send(file=discord.File(f"photos/{random.randrange(1,10)}.jpg"))
        await ctx.message.delete()
        self.Utility.reportAuthor(ctx.command,ctx.author)

    @commands.command()
    async def dog(self,ctx):
        api = "https://dog.ceo/api/breeds/image/random"
        data = requests.get(api)
        data = data.json()
        await ctx.send(data['message'])
        await ctx.message.delete()
        self.Utility.reportAuthor(ctx.command,ctx.author)

    @commands.command()
    async def duck(self, ctx):
        """Returns an image of a duck"""
        api = "https://random-d.uk/api/v2/random"
        data = requests.get(api)
        data = data.json()
        await ctx.send(data['url'])
        await ctx.message.delete()
        self.Utility.reportAuthor(ctx.command,ctx.author)

    @commands.command()
    async def fox(self, ctx):
        """Returns an image of a fox"""
        api = "https://some-random-api.ml/img/fox"
        data = requests.get(api)
        data = data.json()
        await ctx.send(data['link'])
        await ctx.message.delete()
        self.Utility.reportAuthor(ctx.command,ctx.author)

    @commands.command()
    async def whale(self, ctx):
        """Returns an image of a whale"""
        api = "https://some-random-api.ml/img/whale"
        data = requests.get(api)
        data = data.json()
        await ctx.send(data['link'])
        await ctx.message.delete()
        self.Utility.reportAuthor(ctx.command,ctx.author)

    @commands.command()
    async def bird(self, ctx):
        """Returns an image of a bird"""
        api = "https://some-random-api.ml/img/birb"
        data = requests.get(api)
        data = data.json()
        await ctx.send(data['link'])
        await ctx.message.delete()
        self.Utility.reportAuthor(ctx.command,ctx.author)

class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.Utility = Utility(self.bot)

    @commands.command()
    async def xkcd(self,ctx):
        """Returns a random xkcd comic image"""
        request = requests.get("https://random-xkcd-img.herokuapp.com/")
        await ctx.send(request.json()['url'])
        await ctx.message.delete()


    @commands.command(name='8ball')
    async def _8ball(self, ctx):
        """Rolls an 8ball for you"""
        responses = ["No","Mayhaps","Ask again later","Are you dumb? Absolutely not.","Of course silly!","Its a little foggy","It's certain","Huh? I didn't catch that","Never. Not in a million years","I don't see why not?","That just isn't gonna work."]
        self.Utility.reportAuthor(ctx.command,ctx.author)
        await ctx.send(random.choice(responses))

    @commands.command()
    async def quote(self, ctx):
        """Returns a quote from the list of quotes"""
        with open("./quotes","r") as quotes:
            lines = quotes.read().splitlines()
            self.Utility.reportAuthor(ctx.command,ctx.author)
            await ctx.send(random.choice(lines))
        await ctx.message.delete()
        self.Utility.reportAuthor(ctx.command,ctx.author)

    @commands.command()
    async def dance(self, ctx):
        """The bot does a little dance"""
        self.Utility.reportAuthor(ctx.command,ctx.author)
        await ctx.send("ᕕ(⌐■_■)ᕗ ♪♬")
        await ctx.message.delete()

    @commands.command()
    async def coc(self, ctx):
        """Returns a random clash of clans guide"""
        listoguide = ["https://clashofclans.fandom.com/wiki/Flammy%27s_Strategy_Guides","https://medium.com/mr-ways-guide-to-clash-of-clans/clash-of-clans-the-ultimate-beginners-guide-830f6d7e0a74","https://houseofclashers.com/wiki/en/clash-of-clans-builder-base/strategy-guide/beginners-guide/"]
        self.Utility.reportAuthor(ctx.command,ctx.author)
        await ctx.send(random.choice(listoguide))

    @commands.command()
    async def hw(self, ctx, target: str):
        """Tells someone to do their homework"""
        await ctx.send(f"Do your homework {target}!")
        self.Utility.reportAuthor(ctx.command,ctx.author)
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
        self.Utility.reportAuthor(ctx.command,ctx.author)
    
    @commands.command()
    async def cope(self,ctx):
        """Cope"""
        await ctx.send("https://tenor.com/view/cope-dont-care-crying-cry-chips-gif-21606846")
        await ctx.message.delete()
        self.Utility.reportAuthor(ctx.command,ctx.author)

class Utility(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command()
    async def say(self, ctx, *message: str):
        """Parrots back what you say"""
        await ctx.send(" ".join(message))
        await ctx.message.delete()
        self.reportAuthor(ctx.command,ctx.author)

    @commands.command()
    async def poll(self, ctx):
        """Adds a poll to your message"""
        await ctx.message.add_reaction("✅")
        await ctx.message.add_reaction("🚫")
        self.reportAuthor(ctx.command,ctx.author)

    def reportAuthor(self, command: str, author: str):
        print(f"{author} issued the {command} command.")
        
    def getYTURL(self, lnk):
        print(type(lnk))
        lnk = "+".join(lnk)
        q = f"https://www.youtube.com/results?search_query={lnk}"
        print(q)
        html = requests.get(f"https://www.youtube.com/results?search_query={lnk}")
        video_ids = re.findall(r"watch\?v=(\S{11})", html.content.decode())
        return video_ids[0]

      
bot.add_cog(Listeners(bot))
bot.add_cog(Music(bot))
bot.add_cog(Utility(bot))
bot.add_cog(Images(bot))
bot.add_cog(Fun(bot))
print("E")
bot.run(os.getenv('DISCORD-TOKEN'))
