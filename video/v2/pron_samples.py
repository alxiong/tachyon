"""Pronunciation A/B samples for Tachyon / tachygram / psi (cheap, ~100 chars each)."""
import os
from dotenv import load_dotenv
from elevenlabs.client import ElevenLabs

load_dotenv("/home/alex/work/tachyon_wt1/.env")
VOICE_ID = "nPczCjzI2devNBz1zQrb"  # Brian, as v1
SETTINGS = {"stability": 0.38, "similarity_boost": 0.80, "style": 0.45, "use_speaker_boost": True}
SENT = "{T} keeps one accumulator. The note's {P} seeds every nullifier, and each {G} looks the same on chain."
VARIANTS = {  # name: (Tachyon, psi, tachygram)
    "1_tack-ion_sigh":   ("Tack-ion", "sigh", "tack-ion-gram"),
    "2_takyon_psai":     ("Tak-yon", "psai", "tak-yo-gram"),
    "3_tackyon_psy":     ("Tackyon", "psy", "tacky-gram"),
    "4_tack-ih-on_Psi":  ("Tack-ih-on", "Psi", "tack-ih-gram"),
    "5_v1_tack-ee-on_psi": ("Tack-ee-on", "psi", "tack-ee-gram"),
}
client = ElevenLabs(api_key=os.environ["ELEVENLABS_API_KEY"])
for name, (t, p, g) in VARIANTS.items():
    text = SENT.format(T=t, P=p, G=g)
    audio = client.text_to_speech.convert(voice_id=VOICE_ID, text=text, model_id="eleven_multilingual_v2",
                                          output_format="mp3_44100_128", voice_settings=SETTINGS)
    with open(f"audio/samples/{name}.mp3", "wb") as f:
        for chunk in audio: f.write(chunk)
    print(name, "|", text)
sub = client.user.subscription.get()
print(f"usage: {sub.character_count} / {sub.character_limit}")
