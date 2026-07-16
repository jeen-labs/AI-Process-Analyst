import os

from google import genai

client = genai.Client(
    api_key=os.environ["GOOGLE_API_KEY"]
)

print("=" * 80)
print("AVAILABLE GEMINI MODELS")
print("=" * 80)

for model in client.models.list():

    if "generateContent" in getattr(model, "supported_actions", []):

        print(model.name)