"""
API Key Setup Window for LangForge
"""
import customtkinter as ctk
import webbrowser
from typing import Callable

class APIKeyWindow(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.captured_key = None

        self.title("LangForge - Setup")
        self.geometry("450x300")
        self.resizable(False,False)

        self.protocol("WM_DELETE_WINDOW", self._on_closing)

        self._build_ui()

    def _build_ui(self):

        self.title_label = ctk.CTkLabel(self, text="Groq API Key Required", font=("Helvetiva", 20, "bold"), text_color="#3a7ebf")
        self.title_label.pack(pady=(25,10))

        self.desc_label = ctk.CTkLabel(
            self,
            text = ("To protect your security, LangForge requires your own Groq API key.\n"
            "Your key is stored locally on your machine and never shared.\n\n"
            "Note: You are solely responsible for monitoring your API usage, "
            "limits, and any potential billing on your Groq dashboard"),
            font=("Helvetica", 12),
            wraplength=380
        )
        self.desc_label.pack(pady=5)

        self.key_entry = ctk.CTkEntry(self, placeholder_text="Paste your gsk... API key here", width=350, height=40, show="*")
        self.key_entry.pack(pady=10)

        self.save_button = ctk.CTkButton(self, text="Save", font=("Helvetica", 14, "bold"), height=40, width=150, command=self._handle_save)
        self.save_button.pack(pady=15)

    def _handle_save(self):

        api_key = self.key_entry.get().strip()

        if not api_key.startswith("gsk_") or len(api_key) < 10:
            self.title_label.configure(text_color="#C0392B", text="Invalid API Key Format")
            return
        
        self.captured_key = api_key
        self.withdraw()
        self.quit()

    def _on_closing(self):
        #Triggered when the user clicks the native OS close (X) button
        self.quit()

        


    
