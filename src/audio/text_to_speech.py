"""
TTS (Text-to-Speech) Module for Langforge

This script utilizes Silero TTS running strictly on CPU to ensure 0 VRAM usage.
It generates audio tensors directly into memory and streams them to the speaker
via 'sounddevice', avoiding any disk I/O bottlenecks.
"""

import time
import torch
import sounddevice as sd

torch.set_num_threads(4)

class TTSEngine:
    def __init__(self):
        #Initializes the TTS Engine and pre-loads the Silero model into System RAM
        print("Pre-loading Silero TTS model into SYSTEM RAM (CPU). Please wait...")
        self.language = 'en'
        self.model_id = 'v3_en'
        self.sample_rate = 24000
        self.speaker = 'en_0' # Default US Male/Female synthetic voice
        self.device = torch.device('cpu')

        start_load = time.time()

        #Uses torch.hub to download (only once) and cache the model 
        self.model, _ = torch.hub.load(repo_or_dir='snakers4/silero-models',
                                       model='silero_tts',
                                       language=self.language,
                                       speaker=self.model_id)
        self.model.to(self.device)
        print(f"TTS Engine is ready! (Load Time: {time.time() - start_load:.2f}s)\n")
    
    def speak(self, text:str):
        #Converts text to an audio tensor and plays it directly through the speakers.

        if not text or len(text.strip()) == 0:
            print("TTS warning: Empty text received.")
            return
        start_tts = time.time()

        try:
            #Generate audio mathematically (Tensor)
            audio_tensor = self.model.apply_tts(text=text, speaker=self.speaker, sample_rate=self.sample_rate)
            generation_time = time.time() - start_tts
            print(f"Audio generated in {generation_time:.2f}s Playing now...")

            #Convert tensor to numpy array for sounddevice
            audio_np = audio_tensor.numpy()

            #Play audio directly to speaker buffer (Zero I/O disk writes)
            sd.play(audio_np, samplerate=self.sample_rate)
            sd.wait()

        except Exception as e:
            print(f"TTS Generation Error: {e}")

if __name__ == "__main__":

    tts_engine = TTSEngine()

    test_sentences = ["Hello! I am your new AI assistant.",
        "I am running entirely on your local CPU."]
    
    print("-" * 50)
    for sentence in test_sentences:
        print(f"Generating audio for: {sentence}")
        tts_engine.speak(sentence)
        time.sleep(0.5)
    print("-" * 50)
    print("TTS Test completed")