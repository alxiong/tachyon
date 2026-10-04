import os
from dotenv import load_dotenv
from elevenlabs.client import ElevenLabs
load_dotenv("/home/alex/work/tachyon_wt1/.env")
VOICE_ID = "nPczCjzI2devNBz1zQrb"
SETTINGS = {"stability": 0.38, "similarity_boost": 0.80, "style": 0.45, "use_speaker_boost": True}
G = {"g1_tackigram": "tackigram", "g2_tacki-gram": "tacki-gram", "g3_takkigram": "takkigram",
     "g4_tack-ih-gram": "tack ih gram", "g5_tackagram": "tackagram"}
T = {"t1_tacki-on": "Tacki-on", "t2_tackion": "Tackion"}
client = ElevenLabs(api_key=os.environ["ELEVENLABS_API_KEY"])
def say(name, text):
    audio = client.text_to_speech.convert(voice_id=VOICE_ID, text=text, model_id="eleven_multilingual_v2",
                                          output_format="mp3_44100_128", voice_settings=SETTINGS)
    with open(f"audio/samples/{name}.mp3", "wb") as f:
        for c in audio: f.write(c)
    print(name, "|", text)
for n, g in G.items(): say(n, f"Every {g} is thirty-two bytes, and each {g} looks the same on chain.")
for n, t in T.items(): say(n, f"{t} keeps one accumulator for everything.")
s = client.user.subscription.get(); print(f"usage: {s.character_count} / {s.character_limit}")
