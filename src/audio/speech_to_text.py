"""
STT (Speech-to-Text) module for Langforge.

This module utilizes faster-whisper for real-time transcription.
It exposes non-blocking hardware control methods (start_recording, stop_and_transcribe)
to be managed by the main Event-Driven Controller (main.py).
"""

import os
import sys
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

if os.name == 'nt':
    site_packages = os.path.join(sys.prefix, "Lib", "site-packages")
    cublas_bin = os.path.join(site_packages, "nvidia", "cublas", "bin")
    cudnn_bin = os.path.join(site_packages, "nvidia", "cudnn", "bin")
    
    # Prepend the paths so Windows finds these DLLs first
    os.environ["PATH"] = f"{cublas_bin};{cudnn_bin};" + os.environ.get("PATH", "")

import time
import numpy as np
import sounddevice as sd
from faster_whisper import WhisperModel

#Configuration
MODEL_SIZE = "base.en"
SAMPLE_RATE = 16000

class STTEngine:
    def __init__(self):
        "Initializes the STT Engine and pre-loads the models."
        print(f"Pre-loading {MODEL_SIZE} model into memory. Please wait...")
        
        self.model = self._load_model()
        self.audio_data = []
        self.is_recording = False
        self.stream = None

        print("STT Engine is ready!")

    def _check_cuda(self):

        """
        Safely scans the physical file system for NVIDIA CUDA DLLs without initializing the AI engine.
        """
        # Target CUDA core libraries required to ignite the GPU acceleration
        dll_names = ["cublas64_12.dll","cublas64_11.dll"]
        paths = []

        # PyInstaller extracts bundled files into a hidden temporary folder known as _MEIPASS.
        if hasattr(sys, '_MEIPASS'):
            paths.append(sys._MEIPASS)
        
        # If not packaged, dynamically locate the Python 'site-packages' directory
        # to find the NVIDIA libraries installed locally via pip.
        else:
            try:
                import site
                for sp in site.getsitepackages():
                    # Construct the exact path where PyTorch/CTranslate2 stores CUDA binaries
                    paths.append(os.path.join(sp, "nvidia", "cublas", "bin"))
            
            except Exception:
                pass
        
        # Iterate through the gathered paths and verify file existence
        for path in paths:
            if path and os.path.isdir(path):
                for dll in dll_names:
                    if os.path.exists(os.path.join(path,dll)):
                        return True
        
        return False

    def _load_model(self):
        try:

            if self._check_cuda():
                print("Model loaded on GPU")
                return WhisperModel(MODEL_SIZE, device="cuda", compute_type="float16")
            
            else:
                print("Model loaded on CPU")
                return WhisperModel(MODEL_SIZE, device="cpu", compute_type="int8")
        
        except Exception as e:
            print(f"GPU failed ({e})")
            return WhisperModel(MODEL_SIZE, device="cpu", compute_type="int8")

    def _audio_callback(self, indata, _frames, _time_info, status):
        """
        Callback function to collect audio chunks continuously.
        '_frames' and '_time_info' are strictly required by the PortAudio C-library signature.
        they are deliberately unused in this Push-to-Talk (PTT) memory buffer architecture.
        """
        if status:
            print(f"Audio status: {status}")

        if self.is_recording:
            self.audio_data.append(indata.copy())

    def start_recording(self):
        """
        Opens the microphone stream in a non-blocking background thread
        Triggered by the UI controller
        """

        self.audio_data = []
        self.is_recording = True

        self.stream = sd.InputStream(samplerate=SAMPLE_RATE, channels=1, callback=self._audio_callback, dtype="float32")
        self.stream.start()

    def stop_and_transcribe(self) -> str:
        """
        Stops the microphone stream and executes inference directly from RAM. Zero disk I/O involved
        """
        self.is_recording = False

        if self.stream:
            self.stream.stop()
            self.stream.close()
        
        if not self.audio_data:
            print("No audio recorded")
            return ""
        
        #Concatenate audio chunks and save to a temporary WAV file
        audio_np = np.concatenate(self.audio_data, axis=0).flatten() #Flatten from (N,1) to (N,) 1D array as expected by Whisper

        memory_size_kb = audio_np.nbytes / 1024

        print(f"RAM Check: {memory_size_kb:.2f} KB, Shape: {audio_np.shape}")

        if audio_np.size == 0 or np.all(audio_np== 0):
            return ""

        #Transcribe inference
        start_time = time.time()
        
        segments_gen, _ = self.model.transcribe(audio_np, beam_size=5)

        full_text = "".join([segment.text + " " for segment in segments_gen])

        inference_time = time.time() - start_time

        print("-" * 50)
        print(f"STT Inference Time: {inference_time:.2f}s")
        print("-"*50)

        return full_text.strip()
