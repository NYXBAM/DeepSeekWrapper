# DeepSeekClient — UNOFFICIAL Wrapper for DeepSeek

**⚠️ Note:** This project is **for educational and research purposes only**. Do not use it for production or violate terms of service of DeepSeek.

---

## Overview

`DeepSeekClient` is an asynchronous Python wrapper around **Playwright** that allows interaction with the DeepSeek web interface.

It provides:

- A clean client API to send messages and retrieve responses.
    
- Isolation of multiple clients (agents) using **BrowserContext** for concurrent operations.
    
- Support for single-client and multi-agent workflows.
    


---

## Features

1. **Single Client Usage**
    
    - Initialize a client, start a session, send messages, and read responses.
        
2. **Multi-Agent / Multi-Context Usage**
    
    - Use a single browser instance with multiple isolated agents.
        
    - Each agent has its own `BrowserContext` and `Page`.
        
    - Run multiple queries concurrently without race conditions.
        
3. **Asynchronous API**
    
    - Fully async with `asyncio`, making it efficient for IO-bound tasks.
        
4. **Session Management**
    
    - Handles login via storage state.
        
    - Supports clean session start and proper browser shutdown.
        

---

## Installation

```bash
git clone https://github.com/NYXBAM/DeepSeekWrapper.git
cd DeepSeekWrapper

pip install poetry
pipx install poetry # better way
poetry install
# activate venv
source .venv/bin/activate 
# install browser
poetry run playwright install firefox
# create .env 
nano .env
#
# put u login and password in .env 
# DEEPSEEK_LOGIN=
# DEEPSEEK_PASSWORD=
```





---

## Basic Usage — Single Client

```python
import asyncio
from client.ds_cli import DeepSeekClient, DeepSeekFlow
from config import CONFIG

async def main():
    client = DeepSeekClient(**CONFIG)
    await client.start_session(headless=True)

    flow = DeepSeekFlow(client)
    response = await flow.run_query("Hi, who are you?")
    print(response)

    await client.close()

asyncio.run(main())
```

---

## Multi-Agent Usage

```python
import asyncio
from client.ds_cli import DeepSeekClient, DeepSeekFlow
from config import CONFIG

async def main():
    # Create a single browser
    playwright, browser = await DeepSeekClient.create_browser(headless=True)

    # Create multiple agents sharing the same browser
    agents = [DeepSeekClient(browser=browser, **CONFIG) for _ in range(3)]

    # Start a session for each agent (isolated context)
    for agent in agents:
        await agent.start_session()

    # Queries for each agent
    queries = [
        "Hi, who are you?",
        "Tell me a joke",
        "Explain basic algebra briefly"
    ]

    # Run all queries concurrently
    results = await asyncio.gather(*[
        DeepSeekFlow(agent).run_query(q) for agent, q in zip(agents, queries)
    ])

    for i, r in enumerate(results):
        print(f"Agent {i+1} response:\n{r}\n{'-'*50}")

    # Close the browser
    await browser.close()
    await playwright.stop()

asyncio.run(main())
```

---

## Notes

- **Educational purposes only:** This library is intended for learning and experimentation.
    
- **Do not use in production:** Behavior of DeepSeek web interface may change, which could break the wrapper.
    
- **Browser resource management:** One browser instance can support multiple agents, but each agent uses memory for its own BrowserContext and Page.
    
- **Concurrency:** Use `asyncio` for parallel operations. Avoid sharing the same Page across tasks — use isolated contexts instead.
    

---

## Contributing

Feel free to fork, experiment, and improve the wrapper for educational purposes. Pull requests are welcome as long as they **adhere to safe, non-production usage**.
