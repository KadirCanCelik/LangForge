"""
Main Application Controller for Langforge.
This script acts as the Orchestrator (Controller) bridging the UI (View) and the AI Models (Backend).
"""
import sys
import io

# PyInstaller --noconsole compatibility
# In windowed mode (headless console), OS disables sys.stdout and sys.stderr.
# We redirect them to a dummy memory stream (Black Hole) to prevent third-party
# libraries (like PyTorch/Silero) from crashing when they attempt to print logs.
if sys.stdout is None:
    sys.stdout = io.StringIO()

if sys.stderr is None:
    sys.stderr = io.StringIO()

import threading
import queue
from ui.ui import LangForgeUI
from audio.speech_to_text import STTEngine
from audio.text_to_speech import TTSEngine
from llm.llm_engine import LLMEngine
from ui.api_key_window import APIKeyWindow
from utils.config_manager import get_stored_api_key, save_api_key

class ApplicationController:
    """
    Manages the application state, hardware triggers, and sequential execution of the AI pipeline (STT- LLM - TTS )
    """
    def __init__(self):
        self.api_key = get_stored_api_key()

        if not self.api_key:
            print("No local API key detected. Launching Setup Window...")
            self.setup_window = APIKeyWindow()
            self.setup_window.mainloop()

            if self.setup_window.captured_key:
                self.api_key = self.setup_window.captured_key
                self.setup_window.destroy()
                self._initialize_pipeline(self.api_key)
            
            else:
                print("Setup cancelled by user. Exiting system.")

                import sys
                sys.exit(0)
        
        else:
            self._initialize_pipeline(self.api_key)

        

    def _initialize_pipeline(self, api_key: str):
        print("Initializing AI Engines...")

        self.api_key = api_key
        save_api_key(self.api_key)

        self.llm = LLMEngine(api_key=self.api_key)
        self.stt = STTEngine()
        self.tts = TTSEngine()

        self.ui = LangForgeUI(on_record_click=self.handle_user_action)

    def run(self):
        #Starts the Tkinker main event loop
        if hasattr(self, 'ui'):
            self.ui.mainloop()

    def handle_user_action(self):

        """
        Triggered when the user clicks the UI button or presses the Spacebar.
        Routes the action based on the current recording state.
        """

        if not self.ui.is_recording:
            self.ui.update_status("Listening...","listening")
            self.stt.start_recording()

        else:
            self.ui.update_status("AI is talking...","processing")

            # Offload the heavy pipeline to a daemon thread to keep UI responsive
            threading.Thread(target=self._ai_pipeline_worker, daemon=True).start()
    
    def _tts_consumer_worker(self, tts_queue: queue.Queue):
        """
        Constantly listens to the queue for new sentences. Stops and gracefully exits when it receives a 'None (Poison Pill).
        """
        while True:
            chunk = tts_queue.get()

            if chunk is None:
                tts_queue.task_done()
                break

            self.tts.speak(chunk)
            tts_queue.task_done()

    def _ai_pipeline_worker(self):
        """
        Executes the AI logic. Feeds sentences to the TTS queue as soon as they are yielded by the LLm stream.
        """

        try:
            user_text = self.stt.stop_and_transcribe()
            
            if not user_text:
                self.ui.after(0, self.ui.update_status, "Ready (No voice detected)", "ready")
                return
            
            self.ui.after(0, self.ui.append_message, "You", user_text)

            tts_queue = queue.Queue()
            tts_thread = threading.Thread(target=self._tts_consumer_worker, args=(tts_queue,), daemon= True)
            tts_thread.start()

            self.ui.after(0, self.ui.update_status, "AI is talking...", "processing")
            self.ui.after(0, self.ui.start_new_message, "LangForge")

            for sentence in self.llm.generate_response_stream(user_text):
                tts_queue.put(sentence)
                self.ui.after(0, self.ui.stream_text, sentence, "LangForge")

            self.ui.after(0,self.ui.end_message)

            tts_queue.put(None)

            #Wait here until the TTS engine finishes playing the last sentences in the queue.
            #Since this wait occurs in a background thread, the UI remains fully responsive
            tts_thread.join() 
        
        except Exception as e:
            print(f"Pipeline Error: {e}")
            self.ui.after(0, self.ui.append_message, "System Error",str(e))

        finally:
            # Always reset the UI state after execution
            self.ui.after(0, self.ui.update_status, "System Ready", "ready")

if __name__ == "__main__":
    app = ApplicationController()
    app.run()