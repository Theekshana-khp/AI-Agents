import os
from dotenv import load_dotenv
from openai import OpenAI
from google import genai
from groq import Groq
from httpx import request

load_dotenv(override=True)

google_api_key = os.getenv("GOOGLE_API_KEY")
groq_api_key = os.getenv('GROQ_API_KEY')
competitors = []
answers = []

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

gemini = OpenAI(api_key=google_api_key, base_url="https://generativelanguage.googleapis.com/v1beta/openai/")
model_name = "gemini-2.5-flash"
response = gemini.chat.completions.create(model=model_name, messages=messages)
answer = response.choices[0].message.content
competitors.append(model_name)
answers.append(answer)

groq = OpenAI(api_key=groq_api_key, base_url="https://api.groq.com/openai/v1")
model_name = "openai/gpt-oss-120b"
response = groq.chat.completions.create(model=model_name, messages=messages)
answer = response.choices[0].message.content
competitors.append(model_name)
answers.append(answer)

ollama = OpenAI(base_url="http://localhost:11434/v1" , api_key="ollama")
model_name = "llama3.2:latest"
response = ollama.chat.completions.create(model=model_name, messages=messages)
answer = response.choices[0].message.content
competitors.append(model_name)
answers.append(answer)

for competitor, answer in zip(competitors, answers):
    print(f"{competitor}:\n {answer}\n\n")

all_answers = ""
for index, answer in enumerate(answers):
    all_answers += f"# Response from competitor {index+1}:\n{answer}\n\n"

judge = f"""You are judging a competition between {len(competitors)} competitors.
Each model has been given this question:

{request}

Your job is to evaluate each response for clarity and strength of argument, and rank them in order of best to worst.
Respond with JSON, and only JSON, with the following format:
{{"results": ["best competitor name", "second best competitor name", "third best competitor name", ...]}}

Here are the responses from each competitor:

{all_answers}

Now respond with the JSON with the ranked order of the competitors, nothing else. Do not include markdown formatting or code blocks."""

messages = [{"role": "user", "content": judge}]

gemini = OpenAI(api_key=google_api_key, base_url="https://generativelanguage.googleapis.com/v1beta/openai/")
model_name = "gemini-2.5-flash"
response = gemini.chat.completions.create(model=model_name, messages=messages)
answer = response.choices[0].message.content

print(answer)