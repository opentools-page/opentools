Quickstart

OpenTools gives you ready-made toolsets (like Trading) that return consistent outputs.

In this quickstart, you’ll create a working agent that connects to your Alpaca account and returns your account information.

⸻

Get started

1) Install the SDK

Open your terminal. Create a folder called my_agent, set up a virtual environment, and install the minimal dependencies.

uv (recommended)

mkdir my_agent
cd my_agent
uv venv
uv pip install opentools-sdk openai python-dotenv

pip

mkdir my_agent
cd my_agent
python -m venv .venv
source .venv/bin/activate
pip install opentools-sdk openai python-dotenv


⸻

2) Add your API keys to your .env file

OpenTools reads credentials from environment variables. For this quickstart we’ll use Alpaca.

Model API key (OpenAI)
If you already have an OpenAI API key, add it to your .env file.
	•	Navigate to the OpenAI dashboard (API keys section)
	•	Click Create new secret key
	•	Copy the key and store it somewhere safe

If you already export OPENAI_API_KEY globally, you can omit it from .env.

Alpaca API key
	•	Create an Alpaca account (no funding required for paper trading)
	•	In the dashboard homepage, find Your API Keys
	•	Click Generate New Keys
	•	Copy your Key ID and Secret Key

Alpaca only shows the Secret Key once. If you lose it, you must generate a new key pair.

Create a .env file
This quickstart uses paper trading by default. OpenTools does not store credentials.

Create a file named .env in the same folder as main.py:

OPENAI_API_KEY="your_openai_api_key"
ALPACA_KEY="your_alpaca_key_id"
ALPACA_SECRET="your_alpaca_secret_key"


⸻

3) Run your first tool call

You’re about to run a small tool loop:
	•	the LLM decides which trading tool to call
	•	OpenTools executes it
	•	the LLM summarises the result

This example uses paper trading and minimal output.

Create a main.py

import asyncio
import os

from dotenv import load_dotenv
from openai import AsyncOpenAI

from opentools import trading
from opentools.adapters.models.openai import run_with_tools


async def main() -> None:
    load_dotenv()

    client = AsyncOpenAI(api_key=os.environ["OPENAI_API_KEY"])

    service = trading.alpaca(
        api_key=os.environ["ALPACA_KEY"],
        api_secret=os.environ["ALPACA_SECRET"],
        model="openai",
        paper=True,
        minimal=True,
    )

    prompt = "Show my account summary and list any open positions."

    result = await run_with_tools(
        client=client,
        model="gpt-4.1-mini",
        service=service,
        user_prompt=prompt,
    )

    print(result)


if __name__ == "__main__":
    asyncio.run(main())

Run your code

python main.py

If the model doesn’t call tools, structure prompts explicitly around them, e.g.:
	•	"Get my account"
	•	"List positions"
	•	"Show recent orders"
