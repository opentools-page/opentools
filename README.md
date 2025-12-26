## Introduction

TLDR;

Creating an open registry of tools that can be used by LLMS to ensure accurate, up-to-date context

The registry, known as opentools, is designed with a modular architecture - each module is designed
to be able to work independetly of one another. 

The only configuration required from the developer is the use of their own key for the tools that are provided ready-made. For more information on this, please look further into the configuration overview below. Please note that each module has its own readme and details for each of the methods utilised so it is easy to set up.

An example output that you would need to add would resemble this in appearance:

```python 
    tools = trading.alpaca(
        key_id=ALPACA_KEY,
        secret_key=ALPACA_SECRET",
        model="openai",
        framework="langgraph",
    )
```


As shown, this object is compatible with langgraph tools (pydantic_ai is also natively supported). Furthermore, openai is the model provider in this example although gemini, anthropic, ollama and openrouter are also natively supported. The only configuration beyond this is that you supply the auth needed for that service, for ollama just get your free key_id and respective secret_key. Instructions are also provided to help with setup with any of the integrated services. There is a growing roadmap already detailed with additional services (inluding ones already configured), if any might be of interest - go ahead and add a suggestion of your own!


> [!NOTE]  
> This is the Python SDK. A TypeScript-compatible SDK is planned, and will aim to mirror this one as closely as possible.

## Configuration
