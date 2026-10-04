import os
from dotenv import load_dotenv
from openai import AzureOpenAI

load_dotenv()

CHAT_MODEL = os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT")
EMBED_MODEL = os.getenv("AZURE_OPENAI_EMBED_DEPLOYMENT")
AI_ENDPOINT = os.getenv("AI_SERVICES_ENDPOINT")
AI_KEY = os.getenv("AI_SERVICES_KEY")

llm = AzureOpenAI(
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_key=os.getenv("AZURE_OPENAI_KEY"),
    api_version="2024-10-21",
)