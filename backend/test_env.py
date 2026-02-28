import os
from dotenv import load_dotenv

load_dotenv()

openai_key = os.getenv("OPENAI_API_KEY")

if openai_key:
    print(f"✅ SUCCESS! Key loaded. It starts with: {openai_key[:7]}...")
else:
    print("❌ FAILED! Python still cannot find the key. Check the .env file name and location.")