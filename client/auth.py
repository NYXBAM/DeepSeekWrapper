import asyncio
from typing import Optional
from playwright.sync_api import sync_playwright
import os

from .ds_cli import DeepSeekClient

from playwright.async_api import async_playwright
import logging

try:
    from DeepSeekWrapper import config
except:
    import config

logger = logging.getLogger(__name__)



class Auth(DeepSeekClient):
    def __init__(
        self,
        storage_state_path: str,
        login_url: str,
        login: str,
        password: str,
        user_input_placeholder: str,
        password_input_placeholder: str,
        unique_class: str
    ):
        self.STORAGE_STATE_PATH = storage_state_path
        self.LOGIN_URL = login_url
        self.LOGIN = login
        self.PASSWORD = password 
        self.USER_INPUT_PLACEHOLDER = user_input_placeholder
        self.PASSWORD_INPUT_PLACEHOLDER = password_input_placeholder
        self.UNIQUE_CLASS = unique_class

    
    async def login(self):
        playwright_auth = None
        browser_auth = None
        
        try:
            
            logger.info('<==> Trying log in DeepSeek <==>')
            playwright_auth = await async_playwright().start()
            # todo
            if config.BROWSER_TYPE == 'firefox':
                browser_auth = await playwright_auth.firefox.launch(
                    headless=False
                )
            if config.BROWSER_TYPE == 'chromium':
                browser_auth = await playwright_auth.chromium.launch(
                    executable_path='/usr/bin/chromium',
                    headless=True,
                    args=[
                        '--no-sandbox',                
                        '--disable-setuid-sandbox',    
                        '--disable-dev-shm-usage',     
                        '--gpu-sandbox-failures-fatal=no',
                        '--disable-gpu'               
                        ]) 
            
            context_auth = await browser_auth.new_context()
            page_auth = await context_auth.new_page()


            await page_auth.goto(self.LOGIN_URL)
            
            # input data
            await page_auth.get_by_placeholder(self.USER_INPUT_PLACEHOLDER).fill(self.LOGIN)
            await page_auth.get_by_placeholder(self.PASSWORD_INPUT_PLACEHOLDER).fill(self.PASSWORD)

            # press button (Login)
            await page_auth.locator(self.UNIQUE_CLASS).click()

            
            await page_auth.wait_for_url("https://chat.deepseek.com/", timeout=15000) 
            logger.info('<-- Successfully log in -->  ')
            
            os.makedirs(os.path.dirname(self.STORAGE_STATE_PATH), exist_ok=True)
            await context_auth.storage_state(path=self.STORAGE_STATE_PATH)
            
            logger.info(f'<--- Session saved in file: {self.STORAGE_STATE_PATH}')
            
        except Exception as e:
            logger.error(f"<!--- ERROR WHILE LOG IN: {type(e).__name__}\n->>>>{e}")
            
            return
            
        finally:
            if browser_auth:
                await browser_auth.close()
            if playwright_auth:
                await playwright_auth.stop()
            # 0