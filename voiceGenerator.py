import os
from dotenv import load_dotenv
from voicevox import Client
from more_itertools import locate

from googletrans import Translator
translator = Translator()

load_dotenv()

USER = os.getenv("USER").split("#")[0]

def cleanResponse(response):
    #replace name
    name = f"Doctor {USER}"
    if name in response:
        response = response.replace(name, "Doctor")

    #remove actions
    if "*" in response:
        starIndex = list(locate(list(response), lambda x: x == "*"))

        #remove the last item if length of starIndex is not even
        if len(starIndex) % 2 != 0:
            starIndex.pop()
        
        cleanedResponse = []
        for i, index in enumerate(starIndex):
            if i == 0 and index != 0:
                cleanedResponse.append(response[:index])
            elif i % 2 != 0 and i == len(starIndex) - 1:
                cleanedResponse.append(response[index + 1:])
            elif i % 2 != 0:
                cleanedResponse.append(response[index + 1:starIndex[i + 1]])

        response = "".join(cleanedResponse)

    #translate response to japanese
    translatedResponse = translator.translate(response, dest="ja").text

    return translatedResponse

async def generateVoice(text, filename):
    async with Client() as client:
        audio_query = await client.create_audio_query(
            text=text,
            speaker=38 #14, 38 nice voice. 13 daddy voice, 15 mommy voice
        )

        path = f"voices/{filename}.mp3"
        with open(path, "wb") as f:
            f.write(await audio_query.synthesis())