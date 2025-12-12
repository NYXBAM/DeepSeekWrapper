import asyncio
from client.ds_cli import DeepSeekClient, DeepSeekFlow
from config import CONFIG


async def single_client_example():
    """
    Example 1: Single DeepSeekClient usage.
    Classic flow with one client, one session.
    """
    client = DeepSeekClient(**CONFIG)
    try:
        await client.start_session(headless=True)
        flow = DeepSeekFlow(client=client)
        response = await flow.run_query("Hi, who are you?")
        print("Single client response:\n", response)
    except Exception as e:
        print("Error in single client example:", e)


async def multi_agent_example():
    """
    Example 2: Multi-agent usage with a single shared browser.
    Each agent has its own BrowserContext and Page for isolated queries.
    """
    # Start one browser instance
    playwright, browser = await DeepSeekClient.create_browser(headless=True)

    # Create multiple clients (agents) sharing the same browser
    agents = [
        DeepSeekClient(external_browser=browser, **CONFIG)
        for _ in range(3)  # Number of agents
    ]

    # Start a session for each agent
    for agent in agents:
        await agent.start_session()

    # Define queries for each agent
    queries = [
        "Hi, who are you?",
        "Tell me a joke",
        "Explain basic algebra briefly"
    ]

    # Run queries concurrently
    results = await asyncio.gather(*[
        DeepSeekFlow(client=agent).run_query(query)
        for agent, query in zip(agents, queries)
    ])

    # Print each agent's result
    for i, result in enumerate(results):
        print(f"Agent {i+1} response:\n{result}\n{'-'*50}")

    # Close the browser and stop Playwright
    await browser.close()
    await playwright.stop()


async def main():
    # Run single client example
    await single_client_example()

    # Run multi-agent example
    await multi_agent_example()


if __name__ == '__main__':
    asyncio.run(main())
