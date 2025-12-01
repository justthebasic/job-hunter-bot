import json
import asyncio
import os
from urllib.parse import urlparse
from playwright.async_api import async_playwright
from playwright_stealth import Stealth
from openai import AsyncOpenAI
from config import Config
from src.logger import setup_logger
from src.exceptions import NavigationError, ExtractionError

logger = setup_logger(__name__)

class JobScraper:
    """
    Handles browser automation and intelligent data extraction.
    """

    def __init__(self):
        self.openai_client = AsyncOpenAI(api_key=Config.OPENAI_API_KEY)

    def _validate_url(self, url: str) -> bool:
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except ValueError:
            return False

    async def get_page_content(self, url: str, retries: int = 3) -> str:
        """
        Launches browser with persistent context and retrieves page innerText.
        Includes retry logic.
        """
        if not self._validate_url(url):
            logger.error(f"Invalid URL provided: {url}")
            raise NavigationError(f"Invalid URL: {url}")

        logger.info(f"[*] Launching browser with auth state: {Config.AUTH_FILE_PATH}")
        
        async with async_playwright() as p:
            # Launch standard browser (not persistent context)
            browser = await p.chromium.launch(
                channel="chrome",
                headless=True, # Headless is safer now with stealth
                args=["--disable-blink-features=AutomationControlled"]
            )
            
            # Load auth state if it exists
            context_options = {}
            if os.path.exists(Config.AUTH_FILE_PATH):
                context_options["storage_state"] = Config.AUTH_FILE_PATH
                logger.info("[*] Loaded authentication state.")
            else:
                logger.warning("[!] No auth.json found. Running without login state.")

            context = await browser.new_context(**context_options)
            page = await context.new_page()
            
            # Apply Stealth
            stealth = Stealth()
            await stealth.apply_stealth_async(page)
            
            for attempt in range(retries):
                try:
                    logger.info(f"[*] Navigating to {url} (Attempt {attempt + 1}/{retries})...")
                    await page.goto(url, wait_until="domcontentloaded", timeout=30000)
                    
                    await asyncio.sleep(3) 

                    # Intelligent Extraction Strategy:
                    # 1. Try to find the main content container to avoid navbars/footers.
                    # 2. Fallback to body if specific containers aren't found.
                    content_selectors = [
                        "main", 
                        "article", 
                        "[role='main']", 
                        "#job-description", 
                        ".job-description", 
                        ".description"
                    ]
                    
                    raw_text = ""
                    for selector in content_selectors:
                        try:
                            element = await page.query_selector(selector)
                            if element:
                                logger.info(f"[*] Found content using selector: {selector}")
                                raw_text = await element.inner_text()
                                break
                        except Exception:
                            continue
                    
                    # Fallback to body if no specific container found
                    if not raw_text:
                        logger.warning("[!] No specific content container found. Falling back to full body text.")
                        raw_text = await page.evaluate("document.body.innerText")

                    # Basic Cleaning: Remove excessive newlines and whitespace
                    cleaned_text = "\n".join([line.strip() for line in raw_text.splitlines() if line.strip()])
                    
                    if not cleaned_text:
                        raise NavigationError("Retrieved empty page content.")
                        
                    return cleaned_text
                    
                except Exception as e:
                    logger.warning(f"[!] Navigation attempt {attempt + 1} failed: {e}")
                    if attempt == retries - 1:
                        logger.error(f"[!] All navigation attempts failed for {url}")
                        # We do not close context here to allow debugging if needed, 
                        # but in production we might want to.
                        await context.close()
                        raise NavigationError(f"Failed to navigate to {url} after {retries} attempts: {e}")
                    await asyncio.sleep(2) # Wait before retry
            
            await browser.close()
            return ""

    async def parse_job_details(self, raw_text: str) -> dict:
        """
        Uses LLM to extract structured JSON data from raw website text.
        """
        logger.info("[*] Sending raw text to LLM for extraction...")
        
        system_prompt = (
            "You are an expert data extraction agent. "
            "Extract the following fields from the job posting text provided: "
            "Job Title, Company Name, Required Hard Skills, Required Soft Skills, Job Description. "
            "Return the output strictly as a JSON object."
        )

        try:
            response = await self.openai_client.chat.completions.create(
                model="gpt-4o-mini", # Cost-effective and capable
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Analyze this text:\n\n{raw_text[:15000]}"} # Truncate to avoid context limit
                ],
                response_format={"type": "json_object"}
            )
            
            content = response.choices[0].message.content
            if not content:
                raise ExtractionError("LLM returned empty content.")

            data = json.loads(content)
            logger.info("[*] Extraction successful.")
            return data
            
        except Exception as e:
            logger.error(f"[!] LLM Extraction error: {e}")
            raise ExtractionError(f"Failed to extract job details: {e}")