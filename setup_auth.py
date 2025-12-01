import asyncio
from playwright.async_api import async_playwright
from src.logger import setup_logger

logger = setup_logger("AuthSetup")

async def setup_auth():
    """
    Launches a visible browser for the user to log in manually.
    Saves the authentication state to 'auth.json'.
    """
    logger.info("Starting authentication setup...")
    logger.info("A browser window will open. Please log in to LinkedIn (or other target sites).")
    logger.info("When you are finished and logged in, press ENTER in this terminal to save and close.")

    async with async_playwright() as p:
        # Launch browser in headful mode
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()

        # Navigate to LinkedIn login page as a convenience
        await page.goto("https://www.linkedin.com/login")

        # Wait for user to interact
        input(">>> Press ENTER after you have successfully logged in...")

        # Save state
        await context.storage_state(path="auth.json")
        logger.info("Authentication state saved to 'auth.json'.")
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(setup_auth())
