from dotenv import load_dotenv
import discord
from discord import app_commands
from discord.ext import commands
import os
import random

import responseController
import voiceGenerator

load_dotenv()

USER = os.getenv("USER")

'''
========================================== Edit Here =================================================================
'''
#Add your discord name here to user the bot
authorizedUsers = ("XPG05#2294", "EJ64#2545", "Solnah#4238", "SilentDeathSong#4036", "powew · ~ ·#9768", "extrovan#1995")
#Add a message here to tell users they are not allowed to talk to the bot
sendoffMessage = ("No one was talking to you, go away!", "...", "Who are you?", "Don't speak to me, scum...")

#Change this between "True" or "False" depending on whether you want to allow users to save responses...
rateResponse = False
'''
======================================================================================================================
'''

audioNameList = {}

#the getResponse() function takes in a 'message' as a str and returns a str
def getResponse(user_message: str, user, privateMessage, guildId) -> str:
    #clean up user_message to remove ping
    if not privateMessage:
        user_message = " ".join(user_message.split(" ")[1:])

    #return a send off message if user is not authorized to use the bot
    if str(user) not in authorizedUsers:
        return random.choice(sendoffMessage)

    #otherwise generate a response using the AI
    return responseController.response(user_message, user, guildId)

async def sendMessage(message, response, privateMessage):
    try:
        #ping user if it is not a private message
        ping = ""
        if not privateMessage:
            ping = f"<@{message.author.id}> "

        #generate a response and send it
        await message.channel.send(ping + response)

        #ask the user to rate the response
        if rateResponse and response not in sendoffMessage:
            await message.channel.send("*Please save this response if you think it is a good response using the `/save <context_count>` command!*")
    
    except Exception as err:
        print(err)

async def getVoice(response, guildId):
    #create audio file name list if it doesnt exist
    if guildId not in audioNameList:
        audioNameList[guildId] = []

    #clean response
    brokenDownResponse = voiceGenerator.cleanResponse(response).split("\n")

    for i, line in enumerate(brokenDownResponse):
        filename = f"{guildId}_{i}"
        #await voice and message together
        await voiceGenerator.generateVoice(line, filename)
        #append audio file name if it does not exist
        if filename not in audioNameList[guildId]:
            audioNameList[guildId].append(filename)
    
    return len(brokenDownResponse)

def playVoice(voiceChannel, guildId, lineCount, i=0):
    #exit when all voice lines are played
    if i == lineCount:
        return
    #set file name
    filename = f"{guildId}_{i}"
    #increase iteration count
    i += 1
    #play voice
    voiceChannel.play(discord.FFmpegPCMAudio(f"voices/{filename}.mp3"), after=lambda e: playVoice(voiceChannel, guildId, lineCount, i))

#check if it is a private message
def isPrivate(channel):
    if str(channel) == "private":
        return True
    return False

#check if the bot is connected to a voice channel in the server
def isConnectedToVoice(guildId, voiceClients):
    #check if the bot is in a voice channel
    if len(voiceClients) == 0:
        return -1
    #check if the bot is connected to any voice channels in this server
    voiceChannel = list(filter(lambda x: x.guild.id == guildId, voiceClients))
    if len(voiceChannel) == 0:
        return -1
    #return the voice channel
    return voiceChannel[0]

def runDiscordBot():
    TOKEN = os.getenv("DISCORD_TOKEN")
    intents = discord.Intents.default()
    intents.message_content = True
    client = commands.Bot(command_prefix="$", intents=intents)

    @client.event
    async def on_ready():
        print(f"{client.user} is now running!")

    @client.event
    async def on_message(message):
        username = str(message.author)
        user_message = str(message.content)
        channel = str(message.channel)

        #log message events
        print(f"{str(username)}: {user_message} ({channel})")

        #check if it is a private message
        privateMessage = isPrivate(message.channel.type)

        #ignore if the message is sent by this bot
        if message.author == client.user:
            return

        #ignore if bot is not pinged and is not a private message
        if not client.user.mentioned_in(message) and not privateMessage:
            return
        
        #get guild id
        if privateMessage:
            guildId = "private"
        else:
            guildId = str(message.guild.id)

        #get response
        response = getResponse(user_message, message.author, privateMessage, guildId)

        #keep track whether a reply has been sent
        messageSent = False
        #generate voice if bot is connected to a voice channel
        if not privateMessage:
            voiceChannel = isConnectedToVoice(message.guild.id, client.voice_clients)
            if voiceChannel != -1:
                try:
                    lineCount = await getVoice(response, str(message.guild.id))
                    #play sound
                    playVoice(voiceChannel, guildId, lineCount)
                except Exception as e:
                    await message.channel.send("Sorry, something went wrong!")
                    print(e)
                #send response
                messageSent = True
                await sendMessage(message, response, privateMessage)
        
        #send message if don't need to wait for voice to generate
        if not messageSent:
            #send response
            await sendMessage(message, response, privateMessage)
    
    #bot commands
    @client.tree.command(name="help", description="Shows all the commands and a description on how to use them.")
    async def help(interaction: discord.Interaction):
        helpMessage = """
/ping
```
Shows the bot's latency in milliseconds (ms).
```
/save <context_count>
```
Save good responses so that it can be used to improve the AI. <context_count> is an integer, maximum value is 10 as the history only stores up to 10 prompt and completion pairs (includes latest message). If you do not enter any value, the default value is 1. If you enter a value more than the current history count, it would save the maximum amount of responses it can save.
```
/join
```
Join the voice call the user who used this command is in. Therefore, you have to be in a voice channel before using this command.
```
/disconnect
```
Disconnect the bot from the voice channel, if it is currently connected to a voice channel.
```
        """
        await interaction.response.send_message(helpMessage, ephemeral=True)
    
    @client.tree.command(name="ping", description="Shows the bot's latency in milliseconds (ms).")
    async def ping(interaction: discord.Interaction):
        await interaction.response.send_message(f"Pong Doctor!\nHehe...\n*{round(client.latency * 1000)}ms*")
    
    @client.tree.command(name="save", description="Save good responses so that it can be used to improve the AI.")
    @app_commands.describe(context_count="Number of messages to save as context (max: 10)")
    async def save(interaction: discord.Interaction, context_count: str=""):
        #only allow authorized users to use this command
        if str(interaction.user) not in authorizedUsers:
            await interaction.response.send_message(random.choice(sendoffMessage))
            return
        #do not allow the function to run if rateResponse is False
        if not rateResponse:
            await interaction.response.send_message("Responses are not currently being collected!")
            return
        #set default context count to 1
        if context_count == "":
            context_count = str(1)
        #get guild id
        if isPrivate(interaction.channel.type):
            guildId = "private"
        else:
            guildId = str(interaction.guild.id)
        #save response by passing it into the saveResponse() function
        await interaction.response.send_message(responseController.saveResponse(context_count, guildId))
    
    @client.tree.command(name="join", description="Join the voice channel.")
    async def join(interaction: discord.Interaction):
        #only allow authorized users to use this command
        if str(interaction.user) not in authorizedUsers:
            await interaction.response.send_message(random.choice(sendoffMessage))
            return
        #only allow this command to be run in a server
        if isPrivate(interaction.channel.type):
            await interaction.response.send_message("You can only use this command in a server!")
            return
        #ensure user is in a voice channel
        if interaction.user.voice == None:
            await interaction.response.send_message("You need to be in a voice channel to use this command!")
            return
        #if the bot is connected to a voice channel in the current server, disconenct and rejoin
        voiceChannel = isConnectedToVoice(interaction.guild.id, client.voice_clients)
        if voiceChannel != -1:
            await voiceChannel.disconnect()
        #connect to the voice channel
        channel = interaction.user.voice.channel
        await channel.connect()
        await interaction.response.send_message(f"Connected to {channel} voice channel!")
            
    @client.tree.command(name="disconnect", description="Disconnect the bot from the voice channel.")
    async def disconnect(interaction: discord.Interaction):
        #only allow authorized users to use this command
        if str(interaction.user) not in authorizedUsers:
            await interaction.response.send_message(random.choice(sendoffMessage))
            return
        #only allow this command to be run in a server
        if isPrivate(interaction.channel.type):
            await interaction.response.send_message("You can only use this command in a server!")
            return
        #check if the bot is connected to any voice channels in this server
        voiceChannel = isConnectedToVoice(interaction.guild.id, client.voice_clients)
        if voiceChannel == -1:
            await interaction.response.send_message("The bot is currently not in any voice channels!")
            return
        #delete voice file
        currentDirectory = os.getcwd()
        guildId = str(interaction.guild.id)
        if guildId in audioNameList:
            for filename in audioNameList[guildId]:
                path = path = currentDirectory + f"/voices/{filename}.mp3"
                if os.path.exists(path):
                    os.remove(path)
            del audioNameList[guildId]
        #disconnect from voice channel
        await voiceChannel.disconnect()
        await interaction.response.send_message("Successfully disconnected from the voice channel!")

    #dev bot commands
    @client.tree.command(name="kill", description="Shoot Rosmontis in the head with a handgun.")
    async def kill(interaction: discord.Interaction):
        #only allow the admin to close the bot
        if str(interaction.user) != USER:
            await interaction.response.send_message("*blocks the bullet with her tactical equipment*\nHey!\nWhat was that for???")
            return
        await interaction.response.send_message("*dies*")
        await client.close()
    
    @client.tree.command(name="forget", description="Whack Rosmontis in the head so hard you give her a concussion...")
    async def forget(interaction: discord.Interaction):
        #only allow the admin to clear the bot's memory
        if str(interaction.user) != USER:
            await interaction.response.send_message("*dodges the attack...*\nWhat do you think you are doing!")
            return
        #delete history
        responseController.deleteHistory(interaction.guild.id)
        await interaction.response.send_message("*opens her eyes...*\nWh...Where am I???\nWhat happened???")
    
    @client.tree.command(name="sync", description="Sync bot commands.")
    async def sync(interaction: discord.Interaction):
        #only allow the admin to sync the bot commands
        if str(interaction.user) != USER:
            await interaction.response.send_message("Hey!!\nYou are not allowed to do that!!!")
            return
        #sync commands
        try:
            synced = await client.tree.sync()
            await interaction.response.send_message(f"Synced {len(synced)} commands(s)!")
        except Exception as err:
            await interaction.response.send_message("Hmmm...\nSomething went wrong...")
            print(err)
    
    client.run(TOKEN)