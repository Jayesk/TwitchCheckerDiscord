import json
from logging.config import stopListening
import asyncio
import threading
import os
import time
from datetime import datetime
from tracemalloc import stop
import requests
import discord
import discord.ext
from discord.utils import get
from discord.ext import commands, tasks



now = datetime.now()

current_time = now.strftime("%H:%M:%S")
print(current_time)

client = discord.Client()
#path of the config file
JSON_FILE = "config.json"

print(len(client.guilds))


#if the file doesn't exist
if not os.path.exists(JSON_FILE):
    #create it
    with open(JSON_FILE, "w") as f:
        f.write(json.dumps({"servers": []}))

#now the file definitely exists, we can read from it
with open(JSON_FILE, "r") as f:
    #grab the contents into a config variable
    config = json.loads(f.read())

@client.event
async def on_message(message):
    if message.content.startswith("$servers"):
        servers = len(client.guilds)
        await message.channel.send('Notifier is currently in '+str(servers)+' servers!')
    # check if the message has $setup at the star
    if message.content.startswith("$setup "):
        if message.author.guild_permissions.manage_channels == True:
            print(message.author.guild_permissions.manage_channels)
            # process the command
            words = message.content.split(" ")

            # if there aren't 3 words (one is $setup, one is the username, one is the channel) then the user typed the command wrong
            if len(words) != 3:
                await message.channel.send("Usage: $setup {twitch username} {channel you want stream alerts posted in}")
                return # get outta here

            twitchuser = words[1]
            channel_id = words[2].strip("<!#>") #get rid of the characters, since discord channels look like <!#id> and we just want the id
            channelName = twitchuser
            
            await message.channel.send('Channel has been set as '+'https://www.twitch.tv/'+channelName+' and '+"<#"+channel_id+">"+" will now be informed when you go live.")

            # update the config with the new shit
            config["servers"].append([twitchuser, channel_id, False])
            
            # save the config to the file again
            with open(JSON_FILE, "w") as f:
                f.write(json.dumps(config))
            print(config)
        else:
            await message.channel.send('You do not have the required permisions to do this.')


@client.event
async def on_ready():
    asyncio.get_event_loop().create_task(checker())

async def checker():
    while True:
        for i in range(len (config["servers"])):
            server = config["servers"][i]
            # vars
            channelName = server[0]
            channel_id = int(server[1])
            twitchuser = channelName
            # checking
            contents = requests.get('https://www.twitch.tv/'+channelName).content.decode('utf-8')
            is_live = 'isLiveBroadcast' in contents
            # if its not in there then:
            if 'isLiveBroadcast' in contents:
                if not server[2]:
                    # send message
                    print(current_time+": "+channelName+" is live!")
                    await client.get_channel(channel_id).send('https://www.twitch.tv/' +channelName+' is now live!')
                    config["servers"][i][2] = is_live

         
        await asyncio.sleep(180)









client.run('token')

# With thanks to:
# github.com/Jachdich

# PROBLEMS
# How are the users inputs from the command able to be made into simple variables like username and channel? 
# How can the bot be checking on multiple streams at once?
# ^^ Surely it needs multiple processes for each?
