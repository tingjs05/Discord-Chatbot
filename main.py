import os
import discordBot

if __name__ == "__main__":
    #start voicevox engine
    currentDirectory = os.getcwd()
    os.startfile(currentDirectory + "/voicevox_engine/run.exe")
    #run discord bot
    discordBot.runDiscordBot()