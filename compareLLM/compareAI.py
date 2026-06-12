import os
from dotenv import load_dotenv
from openai import OpenAI
from google import genai
from groq import Groq
from httpx import request

load_dotenv(override=True)

google_api_key = os.getenv("GOOGLE_API_KEY")
groq_api_key = os.getenv('GROQ_API_KEY')

if google_api_key:
    print("Google API key is set")
else:
    print("Google API key is not set")

if groq_api_key:
    print(f"Groq API Key exists and begins {groq_api_key[:4]}")
else:
    print("Groq API Key not set (and this is optional)")    

request = "Please come up with a challenging, nuanced question that I can ask a number of LLMs to evaluate their intelligence. "
request += "Answer only with the question, no explanation."
messages = [{"role": "user", "content": request}]

messages

gemini = OpenAI(api_key=google_api_key, base_url="https://generativelanguage.googleapis.com/v1beta/openai/")
model_name = "gemini-2.5-flash"

response = gemini.chat.completions.create(model=model_name, messages=messages)
answer = response.choices[0].message.content

print(answer)

groq = OpenAI(api_key=groq_api_key, base_url="https://api.groq.com/openai/v1")
model_name = "openai/gpt-oss-120b"

response = groq.chat.completions.create(model=model_name, messages=messages)
answer = response.choices[0].message.content

print(answer)