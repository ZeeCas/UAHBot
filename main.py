# main.py
import os
import re
import sys, getopt
import discord
import random
import requests
from discord.ext import commands
import asyncio
import urllib.request
import youtube_dl
from datetime import datetime
from dotenv import load_dotenv
load_dotenv()


youtube_dl.utils.bug_reports_message = lambda: ''

ytdl_format_options = {
    'format': 'bestaudio/best',
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
    'options': '-vn'
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)

class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)
        self.data = data
        self.title = data.get('title')
        self.url = ""

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))
        if 'entries' in data:
            # take first item from a playlist
            data = data['entries'][0]
        filename = data['title'] if stream else ytdl.prepare_filename(data)
        return filename

class Bot:

    try:
        opts, args = getopt.getopt(sys.argv[1:],"t:s",["test","say"])
    except:
        pass
    for opt, arg in opts:
        if opt in ("t","--test"):
            print("Passing")
            pass
            os._exit(0)

    def __init__(self, loop=None):
        self.loop = loop
        self.token = os.getenv('DISCORD-TOKEN')
        self.prefix = ','
        self.bot = commands.Bot(command_prefix=self.prefix, loop=self.loop, fetch_offline_member=False)
    async def run(self):
        @self.bot.event
        async def on_message(message):
            channel = message.channel
            guild = message.guild
            _mes = message.content[len(self.prefix):]
            _mes = _mes.split(" ")
            _mes_list = []
            for item in _mes:
                if item !="":
                    _mes_list.append(item)
            args = _mes_list

            if message.content.lower().startswith("im") or message.content.lower().startswith("i'm") or message.content.lower().startswith("i’m"):
                await channel.send(f"Hi {' '.join(args[1:])} i'm dad")
                print(f"{message.author} : Hi {args[1]} i'm dad")
            if not message.content.lower().startswith(self.prefix):
                return
            else:
                command = _mes_list[0].lower()
                del _mes
                del _mes_list
            try:
                if command == "say":
                    whole_message = ""
                    for i in args[1:]:
                        whole_message = whole_message + " " + i
                    await channel.send(whole_message)
                    await message.delete()
                    sys.stdout.write(f"{self.bot.user.name} said: {whole_message}\n")
                    log = open("say-log.txt","a")
                    log.write(f"{self.bot.user.name} said:{whole_message}\n")
                    log.close()  
                    print(f"{message.author} issued the say command.")

                elif command == "8ball":
                    responses = ["No","Mayhaps","Ask again later","Are you dumb? Absolutely not.","Of course silly!","Its a little foggy","It's certain","Huh? I didn't catch that","Never. Not in a million years","I don't see why not?","That just isn't gonna work."]
                    await channel.send(random.choice(responses))
                    print(f"{message.author} issued the 8ball command.")
                elif command == "quote":
                    quotes = ["\"Do not throw babies\" - Dr.Hannah","\"To know your enemy, you must become your enemy.\" - Some Chinese guy","\“Don’t marry a farrier,\” - Dr. Berry","\“If Kamala Harris becomes president, that will make her the hottest president in history— because I’m not gay\”","\"I want to be a bee ... I want to be a praying mantis, that's how I wanna go\" -- Nolan","\“I want somebody to punish me\” ~Luke","\"I think we should kill them (ewoks) long and painfully\" Dr.Baudry","\"it just needs more quotes to properly work i think\" - Cas","\"Muck!\" \"Muck?\"","\"Coyote of the sandwhich\" -Hayley","\“Don’t you dare steal my turkey thug hat!\”","\"I literally want to get a French minor\" ~Jacob","\"I am going to get canceled because of this,\" - Dr. Bjorne","\"Comments? Questions? Concerns?\" Criminology Teachers, every class","\"When I let my sister do it, I let her use both hands.\" ~Anthony","\“I’m never getting sushi from McDonald’s again,\”","\"Kids don't play Animal Crossing\" My Sister","\"They're not getting more beer into the hands of more people, which in my opinion is not socially optimal\" -Dr. Finck"]
                    await channel.send(random.choice(quotes))
                    print(f"{message.author} issued the quote command.")
                elif command =="yt":
                    query = ""
                    for i in args[1:]:
                        query = query + " " + i
                    query = query.replace(" ","+")
                    html = urllib.request.urlopen(f"https://www.youtube.com/results?search_query={query}")
                    video_ids = re.findall(r"watch\?v=(\S{11})", html.read().decode())
                    await channel.send(f"https://www.youtube.com/watch?v={video_ids[0]}")
                    print(f"{message.author} issued the yt command.")
                elif command == "help":
                    await channel.send("```The commands are : \nsay, \n8ball, \nquote, \npoll, \ndog,cat, fox, whale, duck, bird, \nplay and plyt (play youtube link), \npause, resume, and stop```")
                    print(f"{message.author} issued the help command.")
                elif command == "dance":
                    await channel.send("ᕕ(⌐■_■)ᕗ ♪♬")
                    print(f"{message.author} issued the dance command.")
                elif command =="dog":
                    api = "https://dog.ceo/api/breeds/image/random"
                    data = requests.get(api)
                    data = data.json()
                    await channel.send(data['message'])
                    print(f"{message.author} issued the dog command.")
                elif command =="cat":
                    api = "https://api.thecatapi.com/v1/images/search"
                    data = requests.get(api)
                    data = data.json()
                    await channel.send(data[0]['url'])
                    print(f"{message.author} issued the cat command.")
                elif command == "duck":
                    api = "https://random-d.uk/api/v2/random"
                    data = requests.get(api)
                    data = data.json()
                    await channel.send(data['url'])
                    print(f"{message.author} issued the duck command.")
                elif command == "fox":
                    api = "https://some-random-api.ml/img/fox"
                    data = requests.get(api)
                    data = data.json()
                    await channel.send(data['link'])
                    print(f"{message.author} issued the fox command.")
                elif command == "whale":
                    api = "https://some-random-api.ml/img/whale"
                    data = requests.get(api)
                    data = data.json()
                    await channel.send(data['link'])
                    print(f"{message.author} issued the whale command.")
                elif command == "bird":
                    api = "https://some-random-api.ml/img/birb"
                    data = requests.get(api)
                    data = data.json()
                    await channel.send(data['link'])
                    print(f"{message.author} issued the bird command.")
                elif command == "coc":
                    listoguide = ["https://clashofclans.fandom.com/wiki/Flammy%27s_Strategy_Guides","https://medium.com/mr-ways-guide-to-clash-of-clans/clash-of-clans-the-ultimate-beginners-guide-830f6d7e0a74","https://houseofclashers.com/wiki/en/clash-of-clans-builder-base/strategy-guide/beginners-guide/"]
                    await channel.send(random.choice(listoguide))
                    print(f"{message.author} issued the coc command.")
                elif command == "poll":
                    whole_message = ""
                    for i in args[1:]:
                        whole_message = whole_message + " " + i
                    msg = await channel.send(whole_message)
                    await msg.add_reaction("✅")
                    await msg.add_reaction("🚫")
                    await message.delete()
                    print(f"{message.author} issued the poll command.")
                elif command == "join":
                    VC = message.author.voice.channel
                    global client
                    client = await VC.connect()
                    print(f"{message.author} issued the join command.")
                elif command == "leave":
                    await client.disconnect()
                    await message.add_reaction("👌")
                    print(f"{message.author} issued the leave command.")
                elif command == "play":
                    lsongs = ["heman.mp3","donda.mp3","everlong.mp3","bleachers.mp3","comin.mp3","apache.mp3","vent.mp3","bag.mp3","woodlawn.mp3","john.mp3","drive.mp3","dogdoor.mp3","hesitation.mp3","drivesafe.mp3"]
                    song = random.choice(lsongs)
                    client.play(discord.FFmpegPCMAudio(f"music/{song}"), after=lambda e: print('done', e))
                    await channel.send(f"Now playing {song}")
                    print(f"{message.author} issued the play command.")
                elif command == "plyt":
                    filename = await YTDLSource.from_url(args[1], loop=bot.loop)
                    client.play(discord.FFmpegPCMAudio(filename))
                    print(f"{message.author} issued the plyt command.")
                elif command == "pause":
                    client.pause()
                    print(f"{message.author} issued the pause command.")
                elif command == "resume":
                    client.resume()
                    print(f"{message.author} issued the resume command.")
                elif command == "stop":
                    client.stop()
                    print(f"{message.author} issued the stop command.")
                elif command == "hw":
                    await channel.send(f"Do your homework {args[1]}")
                    await message.delete()
                    print(f"{message.author} issued the hw command.")
                elif command == "bones":
                    bone = requests.get("https://bones-backend.herokuapp.com/bones")
                    bone = bone.json()
                    if bone[0]['value'] == "b":
                        await channel.send("Its a bones day!!!")
                        await message.delete()
                    else:
                        await channel.send("Its a no bones day!!!")
                        await message.delete()
                    print(f"{message.author} issued the bones command.")
                elif command == "wednesday":
                    if (datetime.today().weekday() == 2):
                        await channel.send("Its wednesday my dudes!")
                        await message.delete()
                    else:
                        await channel.send("It is not a wednesday <:sadge:906740836404981790>")
                        await message.delete()
                    print(f"{message.author} issued the wednesday command.")
                elif command == "gas":
                    print("gas")
                elif command == "quit":
                    print("Quitting")
                    os._exit(0) 
                    

            except Exception as e:
                print(e)
                pass
        @self.bot.event
        async def on_ready():
            data = f"Welcome {self.bot.user.name}"
            print(data)
        await self.bot.start(self.token, bot=True)
main_loop = asyncio.get_event_loop()
bot_instances = [
    Bot(loop=main_loop)
]

for bot in bot_instances:
    main_loop.create_task(bot.run())
main_loop.run_forever()