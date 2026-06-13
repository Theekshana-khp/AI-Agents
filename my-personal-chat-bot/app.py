from google import genai
import os
import gradio as gr
from dotenv import load_dotenv

load_dotenv(override=True)

api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    raise ValueError("GOOGLE_API_KEY not found in .env file")

client = genai.Client(api_key=api_key)

with open("2.txt", "r", encoding="utf-8") as f:
    my_details = f.read()

print("=== My Details ===")
print(my_details)


def get_response(message, history):

    history_text = ""
    for user_message, assistant_message in history:
        history_text += f"User: {user_message}\nAssistant: {assistant_message}\n"

    prompt = f"""
    You are my personal AI assistant.

    Use the following information about me to answer questions thinking you are me:

    {my_details}

    Previous Conversation:
    {history_text}

    User Question:
    {message}
    """

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )

    return response.text

gr.ChatInterface(
    fn=get_response,
    title="My Personal Chatbot"
).launch()