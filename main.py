# main.py
import os
import re
import sys, getopt
import discord
import random
from discord.ext import commands
import asyncio
import urllib.request
from dotenv import load_dotenv
load_dotenv()



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
            # if message.channel.name == 'general-hell':
            #     print("General Hell")
            #     if message.author.name == "Yumeko":
            #         print("Yumeko")
            #         await message.channel.send(".pick")
            if not message.content.lower().startswith(self.prefix):
                return
            channel = message.channel
            guild = message.guild
            _mes = message.content[len(self.prefix):]
            _mes = _mes.split(" ")
            _mes_list = []
            for item in _mes:
                if item !="":
                    _mes_list.append(item)
            args = _mes_list
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
                elif command == "scream":
                    await channel.send("AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAHHHHHHHHHHHHHH")
                    await message.delete()
                elif command == "react":
                    for emoji in args:
                        if emoji == "react":
                            print("e")
                        else:
                            await message.add_reaction(emoji)
                elif command == "8ball":
                    responses = ["No","Mayhaps","Ask again later","Are you dumb? Absolutely not.","Of course silly!","Its a little foggy","It's certain","Huh? I didn't catch that","Never. Not in a million years","I don't see why not?","That just isn't gonna work."]
                    await channel.send(random.choice(responses))
                elif command == "quote":
                    quotes = ["\"Do not throw babies\" - Dr.Hannah","\"To know your enemy, you must become your enemy.\" - Some Chinese guy","\“Don’t marry a farrier,\” - Dr. Berry","\“If Kamala Harris becomes president, that will make her the hottest president in history— because I’m not gay\”","\"I want to be a bee ... I want to be a praying mantis, that's how I wanna go\" -- Nolan","\“I want somebody to punish me\” ~Luke","\"I think we should kill them (ewoks) long and painfully\" Dr.Baudry","\"it just needs more quotes to properly work i think\" - Cas","\"Muck!\" \"Muck?\"","\"Coyote of the sandwhich\" -Hayley"]
                    await channel.send(random.choice(quotes))
                elif command =="yt":
                    query = ""
                    for i in args[1:]:
                        query = query + " " + i
                    query = query.replace(" ","+")
                    html = urllib.request.urlopen(f"https://www.youtube.com/results?search_query={query}")
                    video_ids = re.findall(r"watch\?v=(\S{11})", html.read().decode())
                    await channel.send(f"https://www.youtube.com/watch?v={video_ids[1]}")
                elif command == "help":
                    await channel.send("The commands are : say,8ball,quote,react, and yt. yt allows you to search for youtube videos, it chooses the first result.")
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