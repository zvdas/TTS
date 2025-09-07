# file.py
import os
from TTS.api import TTS
from pydub import AudioSegment

# ============================
# Configuration
# ============================

INPUT_FILE = "inputs/affirmations.txt"              # text file with affirmations
SUPPORT_DIR = "support"                             # supporting files (music, etc.)
TEMP_DIR = "temp"                                   # temporary wav files
OUTPUT_DIR = "outputs"                              # final files

BACKGROUND_MUSIC_FILE = os.path.join(SUPPORT_DIR, "meditation_music.mp3")

PAUSE_DURATION_MS = 3000  # pause between affirmations (3 sec)
SPEAKER = "p225"          # female VCTK speaker
SPEED = 0.85              # < 1.0 slower, > 1.0 faster

# ============================
# Setup
# ============================

for folder in [INPUT_FILE, SUPPORT_DIR, TEMP_DIR, OUTPUT_DIR]:
    if not os.path.exists(folder if folder != INPUT_FILE else os.path.dirname(folder)):
        os.makedirs(folder if folder != INPUT_FILE else os.path.dirname(folder))

tts = TTS("tts_models/en/vctk/vits")

# Read affirmations
with open(INPUT_FILE, "r", encoding="utf-8") as f:
    affirmations = [line.strip() for line in f if line.strip()]

# ============================
# Generate affirmations
# ============================

segments = []
for i, text in enumerate(affirmations, start=1):
    filename = os.path.join(TEMP_DIR, f"temp_{i}.wav")

    tts.tts_to_file(
        text=text,
        speaker=SPEAKER,
        speed=SPEED,
        file_path=filename
    )

    seg = AudioSegment.from_wav(filename)
    segments.append(seg)

    if i < len(affirmations):
        segments.append(AudioSegment.silent(duration=PAUSE_DURATION_MS))

    print(f"Generated temp file: {filename}")

# ============================
# Combine & add background
# ============================

# Add 5 seconds of silence at the end
final_audio = sum(segments) + AudioSegment.silent(duration=5000)

if os.path.exists(BACKGROUND_MUSIC_FILE):
    music = AudioSegment.from_file(BACKGROUND_MUSIC_FILE)

    # Loop background if too short
    while len(music) < len(final_audio):
        music += music

    # Trim & fade music to match final length
    music = music[:len(final_audio)].fade_in(2000).fade_out(2000)

    # Lower music volume
    music = music - 15  

    # Overlay voice + music
    final_audio = final_audio.overlay(music)

final_path = os.path.join(OUTPUT_DIR, "meditation_affirmations.mp3")
final_audio.export(final_path, format="mp3")

print(f"✅ Final meditation file saved at: {final_path}")
