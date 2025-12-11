import asyncio
import os

from client.ds_cli import DeepSeekClient, DeepSeekFlow
from config import CONFIG


async def main():
    
    
    # create client
    client = DeepSeekClient(**CONFIG)
    
    try: 
        # start session 
        await client.start_session(headless=True)
        
        # create flow 
        flow = DeepSeekFlow(client=client)
        
        response = await flow.run_query('Hi, who are u?')
        
        print(response)
    
    except Exception as e:
        print(e)
    


if __name__ == '__main__':
    asyncio.run(main())



