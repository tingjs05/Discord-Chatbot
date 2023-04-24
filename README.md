# Instructions to run code

Download the [Voicevox Engine](https://github.com/VOICEVOX/voicevox_engine/releases/tag/0.14.4) and add it to the project folder to be able to generate the voice for the AI. Also, should probably add a `voices` folder to the project folder...

Add an env file to the project folder that contains:
- `DISCORD_TOKEN` (discord API key)
- `GPT_API_KEY` (openAI API key)
- `USER` (discord tag of the owner)

You can edit the code under the "Edit Here" section in `discord.py` to suit your needs.
- Adding the discord tag of users to the `authorizedUsers` to allow them to speak with the bot
- Adding a message to `sendoffMessage` to tell users that they do not have permission to speak with the bot
- Changing the value of `rateResponse` between `True` or `False` depending on whether responses are being collected for fine tuning
  <br>
  (Do take note that you have to extract the files from `fine_tuning.zip` and add it to the project folder for this to work properly)

# Fine Tuning
Do this funny called **EXTRACT `fine_tuning.zip` !!!**
<br>
(Btw everything here is kinda buggy, soooooo yes...)

## Cleaning CSV Files
CSV Files should have two columns, `prompt` and `completion`. Add the CSV file to the `raw_csv_files` from the extracted folder. Then add the file name to `fileName` in `cleanCSV.py`

## Actually Fine Tuning The Thing
Run `fineTunesManager.py` and select the necessary option :)
