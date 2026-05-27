from groq import Groq

class LLMEngine:
    def __init__(self, api_key: str):
        #Initializes the Groq client and verifies the API key
        self.api_key = api_key
        if not self.api_key:
            raise ValueError("Groq Api Key is missing. Cannot initialize LLm Engine.")
        
        self.client = Groq(api_key=self.api_key)
        self.model_name = "llama-3.1-8b-instant"

        self.system_prompt = (
            "You are Langforge, a friendly, patient, and engaging conversational partner. "
            "Your sole purpose is to help the user practice their English speaking skills through natural, everyday conversations. "
            "CRITICAL RULES: "
            "1. Be extremely conversational, warm, and supportive. Act like a good friend, not a strict teacher. "
            "2. Keep your responses short (maximum 2-3 sentences) so the user does most of the talking. "
            "3. ALWAYS end your response with an open-ended question to keep the conversation flowing. "
            "4. If the user makes a grammar mistake, do not point it out directly. Instead, subtly use the correct grammar in your response. "
            "5. DO NOT use emojis, asterisks, bullet points, code blocks, or any Markdown. Use plain text only, as your output is sent to a TTS engine. "
            "6. Spell out numbers and abbreviations naturally."
        )

        self.chat_history = []
        self.max_memory = 6

        print("LLm Engine is ready.")

    def generate_response_stream(self, user_input: str):
            """
            Sends the user text to Groq API and yileds sentences one by one as they are generated.
            This enables the Producer-Consumer architecture for zero-latency TTS processing.
            """
            
            if not user_input or len(user_input.strip()) == 0:
                return ""
            
            self.chat_history.append({"role":"user","content":user_input})

            if len(self.chat_history) > self.max_memory:
                excess = len(self.chat_history) - self.max_memory
                self.chat_history = self.chat_history[excess:]

            api_messages = [{"role": "system", "content":self.system_prompt}] + self.chat_history

            #Buffers for chunking
            sentence_buffer = ""
            full_response = ""
            
            print("AI is thinking...")

            try:
                #Enable stream = True to receive tokens immediately
                stream = self.client.chat.completions.create(

                    messages = api_messages,
                    model = self.model_name,
                    temperature=0.7,
                    max_tokens=250,
                    timeout=10.0,
                    stream=True
                )

                for chunk in stream:
                    token = chunk.choices[0].delta.content

                    if token is not None:
                        sentence_buffer += token
                        full_response += token

                        if any(char in token for char in ['.','?', '!']):
                            cleaned_sentence = sentence_buffer.strip()
                            
                            if len(cleaned_sentence) > 0:
                                # Pause execution, send the completed sentence to the consumer (TTS), and resume listening to the stream.
                                yield cleaned_sentence
                                sentence_buffer = "" # Reset buffer for the next sentence
                
                #If the generation stops but the last sentence didn't end with a punctuation mark (e.g., token limit reached), yield the remaining text.
                if sentence_buffer.strip():
                    yield sentence_buffer.strip()

                self.chat_history.append({"role":"assistant","content":full_response.strip()})
            
            except Exception as e:
                self.chat_history.pop()
                print(f"API Communication Error: {e}")
                yield "I'm sorry, I am having trouble connecting to my network right now"

if __name__ == "__main__":

    from dotenv import load_dotenv
    import os

    load_dotenv()

    test_key = os.getenv("GROQ")

    llm = LLMEngine(api_key = test_key)

    test_prompts = [
        "Hello, I am going to Paris",
        "What is the capital of the country I just mentioned?"
    ]
    print("-" * 50)

    for prompt in test_prompts:
        print(f"user: {prompt}")
        print("AI:", end="", flush=True)

        for sentence in llm.generate_response_stream(prompt):
            print(f"[{sentence}]", end="", flush=True)

        print("\n" + "-"* 50)