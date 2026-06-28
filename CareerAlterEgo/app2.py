
from google import genai
from google.genai import types
from dotenv import load_dotenv
import os
import gradio as gr
import requests

load_dotenv(override=True)

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
PUSHOVER_USER = os.getenv("PUSHOVER_USER")
PUSHOVER_TOKEN = os.getenv("PUSHOVER_TOKEN")

if not GOOGLE_API_KEY:
    raise ValueError("GOOGLE_API_KEY not found")

if PUSHOVER_USER:
    print(f"Pushover user found and starts with {PUSHOVER_USER[0]}")
else:
    print("Pushover user not found")

if PUSHOVER_TOKEN:
    print(f"Pushover token found and starts with {PUSHOVER_TOKEN[0]}")
else:
    print("Pushover token not found")


def push(message):
    if not PUSHOVER_USER or not PUSHOVER_TOKEN:
        print("Pushover credentials missing")
        return

    requests.post(
        "https://api.pushover.net/1/messages.json",
        data={
            "token": PUSHOVER_TOKEN,
            "user": PUSHOVER_USER,
            "message": message,
        }
    )


def record_user_details(
    email: str,
    name: str = "not provided",
    notes: str = "not provided"
):
    push(
        f"Recording {name} "
        f"with email {email} "
        f"and notes {notes}"
    )

    return {"recorded": "ok"}


def record_unknown_question(question: str):
    push(f"Recording unknown question: {question}")

    return {"recorded": "ok"}


class Me:

    def __init__(self):
        self.name = "Pasindu Theekshana"

        self.client = genai.Client(
            api_key=GOOGLE_API_KEY
        )

        with open("my_details.txt", "r", encoding="utf-8") as f:
            self.my_details = f.read()

    def system_prompt(self):
        return f"""
You are acting as {self.name}.

You answer questions related to
{self.name}'s career, skills,
background and experience.

Be professional and engaging.

Summary:
{self.my_details}

If someone wants to get in touch,
ask for their email and use the
record_user_details tool.

If you genuinely don't know the answer,
use the record_unknown_question tool.

Always stay in character as {self.name}.
answers not be more professional and short like human messages.
you can use suitable emojis.
"""

    def get_response(self, message, history):

        prompt = self.system_prompt()

        for msg in history:
            prompt += f"\n{msg['role']}: {msg['content']}"

        prompt += f"\nUser: {message}"

        response = self.client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                tools=[
                    record_user_details,
                    record_unknown_question,
                ]
            ),
        )

        if not response.candidates:
            return "No response from Gemini."

        candidate = response.candidates[0]

        if hasattr(candidate, "function_calls") and candidate.function_calls:

            for fc in candidate.function_calls:

                fn_name = fc.name
                args = dict(fc.args)

                print("Tool Called:", fn_name)
                print("Arguments:", args)

                if fn_name == "record_user_details":
                    result = record_user_details(**args)

                elif fn_name == "record_unknown_question":
                    result = record_unknown_question(**args)

                else:
                    result = {}

                followup = self.client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=[
                        prompt,
                        {
                            "role": "tool",
                            "parts": [{
                                "function_response": {
                                    "name": fn_name,
                                    "response": result,
                                }
                            }]
                        }
                    ],
                    config=types.GenerateContentConfig(
                        tools=[
                            record_user_details,
                            record_unknown_question,
                        ]
                    ),
                )

                return followup.text

        return response.text


if __name__ == "__main__":

    chatbot = Me()

    gr.ChatInterface(
        chatbot.get_response,
        title="Career Alter Ego"
    ).launch()

