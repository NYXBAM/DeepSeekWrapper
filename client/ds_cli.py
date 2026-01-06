import asyncio
import os
import re
from abc import ABC, abstractmethod
import time
from playwright.async_api import async_playwright, Page, BrowserContext, Browser, TimeoutError
from typing import Optional
import logging
from markdownify import markdownify as md

try:
    from DeepSeekWrapper import config
except:
    import config

logger = logging.getLogger(__name__)

# Abstract client interface 

class IWebDriverClient(ABC):
    @abstractmethod
    async def click(self, selector: str) -> None:
        """Clicks on an element specified by the selector."""
        pass

    @abstractmethod
    async def type(self, selector: str, text: str) -> None:
        """Fills an input field specified by the selector."""
        pass

    @abstractmethod
    async def get_by_placeholder(self, text: str) -> 'Locator':
        """Gets a locator for an element with the given placeholder text."""
        pass

    @abstractmethod
    async def locator(self, selector: str) -> 'Locator':
        """Gets a locator for an element specified by the selector"""
        pass

    @abstractmethod
    async def start_session(self, headless: bool = True) -> None:
        """Starts the browser session and navigates to the protected URL."""
        pass

    @abstractmethod
    async def close(self) -> None:
        """Closes the browser and saves state."""
        pass



class DeepSeekClient(IWebDriverClient):
    """
    A Playwright client wrapper for DeepSeek interaction logic.
    Implements IWebDriverClient for architectural flexibility.
    """
    def __init__(
        self,
        storage_state_path: str = None,
        protected_page_url: str = None,
        paragraph_selector: str = None,
        last_paragraph_selector: str = None,
        input_placeholder: str = None,
        button_combo_selector: str = None,
        external_browser = None,
        timeout_seconds: int = 120,
        stability_delay: int = 10
    ):
        self.STORAGE_STATE_PATH = storage_state_path or config.CONFIG.get("storage_state_path")
        self.PROTECTED_PAGE_URL = protected_page_url or config.CONFIG.get("protected_page_url")
        self.PARAGRAPH_SELECTOR = paragraph_selector or config.CONFIG.get("paragraph_selector")
        self.LAST_PARAGRAPH_SELECTOR = last_paragraph_selector or config.CONFIG.get("last_paragraph_selector")
        self.INPUT_PLACEHOLDER = input_placeholder or config.CONFIG.get("input_placeholder")
        self.BUTTON_COMBO_SELECTOR = button_combo_selector or config.CONFIG.get("button_combo_selector")
        
        self.TIMEOUT_SECONDS = timeout_seconds
        self.STABILITY_DELAY = stability_delay
        self.external_browser = external_browser

        self.playwright = None
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        self.lock = asyncio.Lock()

    async def __call__(self, message: str, use_search: bool = False):
        return await self.send_message(message, use_search)

    async def __aenter__(self):
        await self.start_session()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

    async def click(self, selector: str) -> None:
        if not self.page: raise RuntimeError("Session not started.")
        await self.page.click(selector)

    async def type(self, selector: str, text: str) -> None:
        if not self.page: raise RuntimeError("Session not started.")
        await self.page.fill(selector, text)

    async def get_by_placeholder(self, text: str) -> 'Locator':
        if not self.page: raise RuntimeError("Session not started.")
        return self.page.get_by_placeholder(text)

    async def locator(self, selector: str) -> 'Locator':
        if not self.page: raise RuntimeError("Session not started.")
        return self.page.locator(selector)

    async def start_session(self, url=None, headless=True):
        if url is None:
            url = self.PROTECTED_PAGE_URL
        if not os.path.exists(self.STORAGE_STATE_PATH):
            logger.info("<=> You are not logged, trying log in...")
            from .auth import Auth
            auth_cl = Auth(**config.auth_config) 
            await auth_cl.login()
            
        if self.external_browser is None:
            self.playwright = await async_playwright().start()
            self.browser = await self.playwright.firefox.launch(headless=headless)
        else:
            self.browser = self.external_browser
            
        self.context = await self.browser.new_context(storage_state=self.STORAGE_STATE_PATH)
        self.page = await self.context.new_page()
        await self.page.goto(url)
    
    @classmethod
    async def create_browser(cls, headless=True):
        pw = await async_playwright().start()
        browser = await pw.firefox.launch(headless=headless)
        return pw, browser

    async def close(self):
        if self.context:
            await self.context.storage_state(path=self.STORAGE_STATE_PATH)
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()


    # --- DeepSeek Logic Specific Methods ---    
    
    async def wait_for_stable_response(self, start_paragraph_count: int) -> str:
        if not self.page: 
            raise RuntimeError("Session not started.")

        new_paragraph = self.page.locator(self.PARAGRAPH_SELECTOR).nth(start_paragraph_count)
        
        try:
            await new_paragraph.wait_for(state="visible", timeout=50000)
        except Exception as e:
            return f"\nCritical error: {e}"

        start_time = time.time()
        last_html = ""
        stable_since = 0
    
        response_container = self.page.locator(".ds-markdown").last

        while time.time() - start_time < self.TIMEOUT_SECONDS:
            try:
                
                current_html = await response_container.inner_html()
                
                if current_html != last_html:
                    last_html = current_html
                    stable_since = time.time()
                
                if time.time() - stable_since >= self.STABILITY_DELAY and current_html != "":
                    break
                
                await asyncio.sleep(0.5)
            except Exception:
                await asyncio.sleep(0.5)

        if time.time() - start_time >= self.TIMEOUT_SECONDS:
            return f"\nText did not stabilize within {self.TIMEOUT_SECONDS}s."

        
        final_html = await response_container.inner_html()
        cleaned = md(
            final_html,
            heading_style="ATX",  
            bullets="-",         
            code_language_callback=lambda el: el.get('class', '').replace('language-', '') if el.get('class') else None
        )

        return cleaned.strip()
        
    
    async def send_message(self, message: str, use_search: bool = False) -> str:
        async with self.lock:
            if not self.page:
                raise RuntimeError("Session not started. Use start_session().")

            current_count = await (await self.locator(self.PARAGRAPH_SELECTOR)).count()
            if use_search:
                # search_btn = self.page.locator(self.SEARCH_TOGGLE_SELECTOR)
                search_btn = self.page.get_by_role("button", name="Search")
                if await search_btn.is_visible():
                    await search_btn.click()
                    await asyncio.sleep(0.5)
            input_field = self.page.get_by_placeholder(self.INPUT_PLACEHOLDER)
            send_button = self.page.locator(self.BUTTON_COMBO_SELECTOR)

            await input_field.fill(message)
            # await send_button.click()
            await input_field.press("Enter")


            response = await self.wait_for_stable_response(current_count)
            return response



class DeepSeekFlow:
    # This class depends only on the IWebDriverClient interface
    def __init__(self, client: IWebDriverClient):
        self.client = client
        
    async def run_query(self, query: str) -> str:
        return await self.client.send_message(query)

