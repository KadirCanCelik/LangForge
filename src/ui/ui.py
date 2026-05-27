import customtkinter as ctk
from typing import Callable

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class LangForgeUI(ctk.CTk):
    def __init__(self, on_record_click: Callable = None):

        super().__init__()

        self.on_record_click = on_record_click #The controller function triggered when the record button or Spacebar is pressed
        self.is_recording = False

        self.title("LangForge - Speaking Friend")
        self.geometry("550x700")
        self.resizable(False, False)

        self._build_ui()
        self._bind_events()


    def _build_ui(self):

        self.header_label = ctk.CTkLabel(self, text="LangForge AI", font=("Helvetica",24,"bold"),text_color="#3a7ebf")
        self.header_label.pack(pady=(20, 5))

        self.status_label = ctk.CTkLabel(self, text = "System Ready", font=("Helvetica",14))
        self.status_label.pack(pady=(0, 15))

        self.chat_box = ctk.CTkTextbox(self, state="disabled", wrap="word", font=("Helvetica", 15),corner_radius=10)
        self.chat_box.pack(pady=10, padx=20, fill="both", expand=True)

        self.chat_box.tag_config("right_text", justify="right")
        self.chat_box.tag_config("right_name", justify="right", foreground="#3a7ebf")

        self.chat_box.tag_config("left_text", justify="left")
        self.chat_box.tag_config("left_name", justify="left", foreground="#2ecc71")

        self.record_button = ctk.CTkButton(
            self,
            text = "Press Space to Speak",
            font=("Helvetica", 16, "bold"),
            height=60,
            corner_radius=30,
            command=self._handle_interaction
        )
        self.record_button.pack(pady=(10, 30), padx=40, fill="x")

    def _bind_events(self):
        #Binds keyboard events to UI actions.
        self.bind("<space>",self._handle_interaction)


    def _handle_interaction(self, event = None):
        """
        Catches both button clicks and Spacebar presses.
        Delegates the action to the controller.

        'event=None' makes this method polymorphic. 
        - Mouse clicks call this without arguments (uses default None).
        - Keyboard bindings (<space>) automatically pass a Tkinter Event object.
        """
        if self.on_record_click:
            self.on_record_click()

    def update_status(self, text:str, state:str):

        self.status_label.configure(text=text)

        if state == "ready":
            self.status_label.configure(text_color="white")
            self.record_button.configure(text = "Press Space to Speak", state = "normal", fg_color=["#3a7ebf", "#1f538d"])
            
            self.is_recording = False

        elif state == "listening":
            self.status_label.configure(text_color="#C0392B")
            self.record_button.configure(text = "Press Space to Stop", state="normal", fg_color="#C0392B", hover_color="#922B21")

            self.is_recording = True

        elif state == "processing":
            self.status_label.configure(text_color="#F39C12")
            self.record_button.configure(text="AI is talking...", state="disabled", fg_color="#4A4A4A",text_color_disabled="#2ecc71")

            self.is_recording = False

    def append_message(self,sender: str, text: str):
        """
        Appends a new message to the chat box using a Lock/Unlock mechanism.
        
        By default, the text box is 'disabled' to prevent manual user input, 
        maintaining the strictly voice-based nature of the application. 
        This method temporarily changes the state to 'normal' for the exact 
        millisecond needed to insert the text programmatically, and then 
        immediately locks it back to 'disabled' to prevent user interference.
        """

        self.chat_box.configure(state="normal")

        if sender == "You":
            name_tag = "right_name"
            text_tag = "right_text"
        else:
            name_tag = "left_name"
            text_tag = "left_text"
        
        self.chat_box.insert("end",f"{sender}:\n",name_tag)
        self.chat_box.insert("end",f"{text}\n\n",text_tag)

        self.chat_box.configure(state="disabled")
        self.chat_box.see("end")

    def start_new_message(self, sender: str):
        """
        Initializes a new message block for streaming.
        Inserts the sender's name and prepares the text box for incoming chunks
        """

        self.chat_box.configure(state="normal")

        if sender == "You":
            name_tag = "right_name"

        else:
            name_tag = "left_name"
        
        self.chat_box.insert("end",f"{sender}:\n", name_tag)
        self.chat_box.configure(state="disabled")
        self.chat_box.see("end")

    def stream_text(self,text: str, sender: str = "LangForge"):
        """
        Append a chunk of text (sentence) to the currently active message block.
        """
        self.chat_box.configure(state="normal")

        if sender == "You":
            text_tag = "right_text"

        else:
            text_tag = "left_text"

        self.chat_box.insert("end", f"{text}", text_tag)
        self.chat_box.configure(state="disabled")
        self.chat_box.see("end")

    def end_message(self):
        """
        Adds a double newline after a stream is fully completed 
        to separate it visually from the next interaction block.
        """
        self.chat_box.configure(state="normal")
        self.chat_box.insert("end", "\n\n")
        self.chat_box.configure(state="disabled")
        self.chat_box.see("end")

if __name__ == "__main__":

    def mock_action():
        print("Action triggered via Button or Spacebar! Signal sent to Backend")

    app = LangForgeUI(on_record_click=mock_action)
    app.append_message("LangForge", "Hello! Press space to start")
    app.mainloop()