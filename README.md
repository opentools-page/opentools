# Quickstart

OpenTools provides ready-made toolsets (such as **Trading**) that return consistent, structured outputs across models and frameworks.

In this quickstart, you’ll build a minimal agent that connects to your **Alpaca** account and returns account information using OpenAI.

---

## Get started

### 1. Install the SDK

Open a terminal, create a new project folder, set up a virtual environment, and install the required dependencies.

#### Using `uv` (recommended)

```bash
mkdir my_agent
cd my_agent
uv venv
uv pip install opentools-sdk openai python-dotenv
```

#### Using `pip`

```bash
mkdir my_agent
cd my_agent
python -m venv .venv
source .venv/bin/activate
pip install opentools-sdk openai python-dotenv
```

Using a virtual environment ensures this demo stays isolated from your other projects.

---

### 2. Add your API keys

OpenTools reads credentials from environment variables.  
This quickstart uses **Alpaca** for trading and **OpenAI** as the model provider.

#### OpenAI API key

If you already have an OpenAI API key, add it to your environment.

Steps:
- Go to the OpenAI dashboard (API keys section)
- Click **Create new secret key**
- Copy the key and store it somewhere safe

If you already export `OPENAI_API_KEY` globally, you can omit it from the `.env` file.

#### Alpaca API key

Steps:
- Create an Alpaca account (paper trading requires no funding)
- From the dashboard homepage, find **Your API Keys**
- Click **Generate New Keys**
- Copy:
  - **Key ID**
  - **Secret Key**

> **Note**  
> Alpaca only shows the secret key once. If you lose it, you must generate a new key pair.

#### Create a `.env` file

This quickstart uses **paper trading** by default.  
OpenTools does not store credentials or manage OAuth. All keys remain local.

Create a file named `.env` in the same directory as `main.py`:

```env
OPENAI_API_KEY="your_openai_api_key"
ALPACA_KEY="your_alpaca_key_id"
ALPACA_SECRET="your_alpaca_secret_key"
```

---

### 3. Run your first tool call

You’re about to run a small **tool loop**:

- The LLM decides which trading tool to call
- OpenTools executes the tool
- The LLM summarises the result

This example uses **paper trading** and **minimal output**.

#### Create `main.py`

```python
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
```

#### Run the script

```bash
python main.py
```

If the model does not call tools, make the prompt more explicit, for example:

- `Get my account`
- `List positions`
- `Show recent orders`
