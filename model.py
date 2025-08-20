import subprocess
from faster_whisper import WhisperModel
from TTS.api import TTS
from dotenv import load_dotenv
import os
import google.generativeai as genai
import re
import datetime
import logging

# Suppress verbose logs from libraries
logging.getLogger("faster_whisper").setLevel(logging.WARNING)
logging.getLogger("TTS").setLevel(logging.WARNING)
logging.getLogger("numba").setLevel(logging.WARNING)

# Set environment variable for TTS to reduce logging output
os.environ["TTS_LOG_LEVEL"] = "ERROR"

# Load environment variables from .env file
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    print("ERROR: GEMINI_API_KEY not found in environment variables.")
    exit(1)
genai.configure(api_key=GEMINI_API_KEY)

def unique_filename(prefix="file", ext=".wav"):
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{prefix}_{timestamp}{ext}"

def clean_text(text: str) -> str:
    # Remove markdown/special chars like * _ # `
    text = re.sub(r'[\*\_#\`]', '', text)
    # Replace multiple spaces with a single space
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def record_audio_ffmpeg_async(filename, mic_name):
    command = [
        "ffmpeg",
        "-y",
        "-f", "dshow",
        "-i", mic_name,
        "-ar", "16000",
        "-ac", "1",
        filename
    ]
    proc = subprocess.Popen(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return proc

def transcribe_audio(filename):
    try:
        model = WhisperModel("base")
        segments, _ = model.transcribe(filename)
        transcription = " ".join([segment.text for segment in segments])
        # Only print the final transcription
        print("Transcribed text:", transcription)
        return transcription
    except Exception as e:
        print("ERROR: Transcription failed:", e)
        exit(1)

def get_gemini_response(prompt):
    try:
        model = genai.GenerativeModel("gemini-2.0-flash")
        response = model.generate_content(prompt)
        cleaned = clean_text(response.text)
        # Print only the cleaned response text
        print("Response text:", cleaned)
        return cleaned
    except Exception as e:
        print("ERROR: Gemini API request failed:", e)
        print("Please check your internet connection and API key, then try again.")
        return None

def speak_text_coqui(text):
    tts = TTS("tts_models/en/ljspeech/glow-tts", gpu=False)
    filename = unique_filename("response", ".wav")
    print(f"[INFO] Synthesizing speech to {filename}...")
    tts.tts_to_file(text=text, file_path=filename)

    command = ["ffplay", "-autoexit", "-nodisp", filename]
    subprocess.run(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    return filename

if __name__ == "__main__":
    mic_device_name = "audio=Internal Microphone (Cirrus Logic Superior High Definition Audio)"  # Change to your mic device
    recorded_filename = unique_filename("recording", ".wav")

    print("Recording started. Press ENTER to stop recording.")
    ffmpeg_process = record_audio_ffmpeg_async(recorded_filename, mic_device_name)

    input()  # Wait for user to press Enter
    print("Stopping recording...")
    ffmpeg_process.terminate()
    ffmpeg_process.wait()
    print(f"Recording saved: {recorded_filename}")

    transcript = transcribe_audio(recorded_filename)
    if not transcript.strip():
        print("ERROR: Transcription resulted in empty text.")
        exit(1)

    gemini_reply = get_gemini_response(transcript)
    if gemini_reply is None:
        print("Failed to get response from Gemini API. Exiting.")
        exit(1)

    if not gemini_reply.strip():
        print("ERROR: Gemini response is empty.")
        exit(1)

    speak_text_coqui(gemini_reply)
    print("Response spoken successfully.")
