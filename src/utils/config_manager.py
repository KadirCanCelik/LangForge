"""
Handles secure local storage of the user2s API keys inside the OS AppData directory
"""

import os
import json

APP_DIR = os.path.join(os.environ.get("APPDATA",os.path.expanduser("~")),"LangForge")
CONFIG_FILE = os.path.join(APP_DIR,"config.json")

def get_stored_api_key() -> str:
    """
    Retrieves the stored Groq API key from the local config file
    """
    if os.path.exists(CONFIG_FILE):

        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data.get("GROQ_API_KEY","").strip()
        
        except Exception as e:
            print(f"Error reading config file: {e}")
            return ""
        
    return ""

def save_api_key(api_key: str) -> bool:
    """
    Saves the Groq API key to the local config file securely
    """
    if not api_key or len(api_key.strip()) < 10:
        return False
    try:
        if not os.path.exists(APP_DIR):
            os.makedirs(APP_DIR)

        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump({"GROQ_API_KEY": api_key.strip()}, f, indent=4)

        return True
    
    except Exception as e:
        print(f"Error writing config file: {e}")
        return False
