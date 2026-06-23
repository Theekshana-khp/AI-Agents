from io import BytesIO
import requests
from autogen_agentchat.messages import TextMessage, MultiModalMessage
from autogen_core import Image as AGImage
from PIL import Image
import asyncio
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_agentchat.agents import AssistantAgent
from autogen_core import CancellationToken
from pandas.core.methods import describe
from pydantic import BaseModel, Field
from typing import Literal
from dotenv import load_dotenv

load_dotenv(override=True)

url = "https://edwarddonner.com/wp-content/uploads/2024/10/from-software-engineer-to-AI-DS.jpeg"

pil_image = Image.open(BytesIO(requests.get(url).content))
img = AGImage(pil_image)

multi_modal_message = MultiModalMessage(content=["Describe the content of this image in detail", img], source="User")

class ImageDescription(BaseModel):
    scene: str = Field(description="Briefly, the overall scene of the image")
    message: str = Field(description="The point that the image is trying to convey")
    style: str = Field(description="The artistic style of the image")
    orientation: Literal["portrait", "landscape", "square"] = Field(description="The orientation of the image")

model_client = OpenAIChatCompletionClient(model="gpt-4o-mini")
describer = AssistantAgent(
    name="description_agent",
    model_client=model_client,
    system_message="You are good at describing images",
    output_content_type=ImageDescription
)

async def main():
    response = await describer.on_messages(
        [multi_modal_message],
        cancellation_token=CancellationToken()
    )

    reply = response.chat_message.content

    print(reply.scene)
    print(reply.message)
    print(reply.style)
    print(reply.orientation)

asyncio.run(main())

