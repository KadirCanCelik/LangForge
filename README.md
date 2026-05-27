<div align="center">
  <h1> LangForge</h1>

  <p>
    <img src="https://img.shields.io/badge/Python-3.10+-blue.svg" alt="Python">
    <img src="https://img.shields.io/badge/GUI-CustomTkinter-1f425f.svg" alt="CustomTkinter">
    <img src="https://img.shields.io/badge/LLM-Groq_API-f55036.svg" alt="Groq">
    <img src="https://img.shields.io/badge/STT-Faster_Whisper-00a67d.svg" alt="Faster-Whisper">
    <img src="https://img.shields.io/badge/TTS-Silero-ffb000.svg" alt="Silero">
  </p>

  <p><b>Zero-latency, privacy-first AI English speaking friend desktop application.</b></p>
</div>

---

## ✨ Why LangForge?

LangForge is not just another generic voice assistant; it is a highly optimized, real-time **English Speaking Friend** designed to help you practice conversations naturally. It achieves true zero-latency and maximum privacy through advanced engineering choices.

### Biometric Data Privacy & Token Optimization
Your voice is your biometric data, and with LangForge, it never leaves your machine. Audio is entirely processed by the local STT engine. Only the resulting plain text is sent to the LLM API. This architecture guarantees **100% privacy for your voice footprint** while completely avoiding the massive costs associated with multimodal (audio) API calls, consuming only the most cost-effective unit: text tokens.

### Asynchronous Streaming & Instant Synthesis
LangForge does not wait for the LLM to generate a complete response before speaking. The incoming text stream is captured sentence-by-sentence and immediately piped into the local TTS (Silero) engine. This drastic optimization in **Time-to-First-Audio (TTFA)** means you hear the beginning of the AI's sentence while it is still generating the end. The result is true zero-latency, creating the seamless, uninterrupted feel of conversing with a real human.

### Zero-Latency Audio Pipeline
Traditional voice applications save audio to disk before processing, introducing noticeable lag. LangForge completely bypasses disk I/O. Voice data is captured via sounddevice and processed directly in RAM as NumPy arrays, instantly feeding the local STT engine.

### Bring Your Own Key (BYOK)
For the intelligent conversation generation, LangForge uses a BYOK model. No API keys are hardcoded; users simply input their Groq API key directly into the application interface upon launch, ensuring total control over their LLM usage.

### Dual-Release Strategy
Tailored builds are provided to ensure optimal performance regardless of the hardware:
* **CPU Version (~1 GB):** Universal compatibility for any system.
* **GPU Version (~1.8 GB):** Specifically optimized and bundled with CUDA dependencies for maximum hardware acceleration on NVIDIA GPUs.

---

## 🏗 System Architecture

1. **Input:** User voice is captured in real-time straight into memory (RAM).
2. **STT (Local):** faster-whisper transcribes the in-memory audio into text locally, protecting biometric data.
3. **LLM Stream (Cloud/BYOK):** The text is sent to the high-speed Groq API. The response is streamed back asynchronously.
4. **TTS Synthesis (Local):** As sentences are streamed from the LLM, they are instantly synthesized into human-like speech using torchaudio and Silero TTS.
5. **Output:** The generated speech is played back instantly, achieving optimal Time-to-First-Audio.

---

## 🛠 Tech Stack

| Component | Technology | Description |
| :--- | :--- | :--- |
| **GUI** | `customtkinter` | Modern, dark-mode friendly desktop interface. |
| **Audio I/O** | `sounddevice`, `numpy` | Diskless, direct RAM audio capturing and playback. |
| **STT Engine** | `faster-whisper`, `ctranslate2` | Optimized, local Speech-to-Text inference. |
| **LLM Engine** | `groq` | High-speed cloud LLM (Requires API key). |
| **TTS Engine** | `torch`, `torchaudio`, `omegaconf` | Silero Text-to-Speech for natural voice generation. |
| **Config & Secrets**| `python-dotenv` | Secure API key and configuration management. |
| **Packaging** | `pyinstaller` | One-Dir architecture. |

---

## 📥 Installation & Setup

### For End-Users (Pre-built Binaries)

1. Navigate to the [Releases](https://github.com/KadirCanCelik/LangForge/releases) page.
2. Download the appropriate version for your system:
   * `LangForge_CPU.zip` (For general machines)
   * `LangForge_GPU_Nvidia.7z` (For NVIDIA GPUs)
3. Extract the archive using 7-Zip or WinRAR.
4. Run the `LangForge.exe` executable.
5. Upon launch, enter your Groq API key into the designated textbox in the user interface to start practicing your English.

### For Developers (Source Code)

If you wish to build, modify, or run LangForge directly from the source code:

**1. Clone the repository:**
```bash
git clone [https://github.com/KadirCanCelik/LangForge.git](https://github.com/KadirCanCelik/LangForge.git)
cd LangForge
```

**2. Create and activate a virtual environment:**
```bash
python -m venv venv
# On Windows
venv\Scripts\activate
# On macOS/Linux
source venv/bin/activate
```

**3. Install dependencies:**
```bash
pip install -r requirements.txt
```

**4. Run the application:**
```bash
python src/main.py
```
