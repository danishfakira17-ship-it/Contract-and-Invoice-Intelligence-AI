import os
from dotenv import load_dotenv
from openai import AzureOpenAI

load_dotenv()

client = AzureOpenAI(
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_key=os.getenv("AZURE_OPENAI_KEY"),
    api_version="2024-10-21",
)

chat = client.chat.completions.create(
    model=os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT"),
    messages=[{"role": "user", "content": "In one sentence, what is an invoice?"}],
)
print("CHAT OK:", chat.choices[0].message.content)

emb = client.embeddings.create(
    model=os.getenv("AZURE_OPENAI_EMBED_DEPLOYMENT"),
    input="payment terms net 30",
)
print("EMBEDDING OK, vector size:", len(emb.data[0].embedding))