from TTS.api import TTS

# Voice descriptions: key is model name, value is a dict with info and demo speakers
MODEL_DESCRIPTIONS = {
    "tts_models/en/vctk/vits": {
        "desc": "Multi-speaker VITS, UK/US accents, male & female voices.",
        "demo_speakers": ["p225", "p226"]  # Example: p225=female, p226=male (see docs for more)
    },
    "tts_models/en/ljspeech/tacotron2-DDC": {
        "desc": "Single-speaker, LJSpeech (US English, female).",
        "demo_speakers": []
    },
    "tts_models/en/ljspeech/glow-tts": {
        "desc": "Single-speaker, neural Glow-TTS (US English, female).",
        "demo_speakers": []
    }
}

sample_text = "This is a test of the voice you are currently hearing. Choose the one you like best for your project."

for model_name, opts in MODEL_DESCRIPTIONS.items():
    print(f"\nTesting model: {model_name}")
    tts = TTS(model_name)
    desc = opts["desc"]
    # Announce which model is being played
    announcement = f"You are now hearing: {desc}"
    combined_text = announcement + " " + sample_text

    # For multi-speaker models, test the listed demo speakers
    if tts.speakers:
        for speaker in opts.get("demo_speakers", tts.speakers[:2]):  # Default: first two speakers
            print(f"  Trying speaker: {speaker}")
            filename = f"{model_name.split('/')[-2]}_{speaker}.wav".replace("-", "_")
            tts.tts_to_file(text=combined_text, speaker=speaker, file_path=filename)
            print(f"    Played: {desc} | Speaker: {speaker} | Saved as: {filename}")
    else:
        filename = f"{model_name.split('/')[-2]}.wav".replace("-", "_")
        tts.tts_to_file(text=combined_text, file_path=filename)
        print(f"    Played: {desc} | Saved as: {filename}")

print("\nDone! Listen to the saved wav files to compare and pick your favorite.")
