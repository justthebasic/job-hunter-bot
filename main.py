import asyncio
import os
from config import Config
from src.scraper import JobScraper
from src.cv_generator import CVTailor
from src.submitter import ApplicationSubmitter
from src.logger import setup_logger
from src.exceptions import JobHunterError

# Initialize Logger
logger = setup_logger()

async def main():
    # 1. Validation and Setup
    try:
        Config.validate()
    except ValueError as e:
        logger.error(f"Configuration Error: {e}")
        return

    # User Input (In a real scenario, this might come from a queue or database)
    target_url = input("Enter the Job Posting URL: ").strip()
    if not target_url:
        logger.warning("URL is required.")
        return

    # Initialize Modules
    scraper = JobScraper()
    tailor = CVTailor()

    logger.info("--- Starting Phase 1 & 2: Browser Automator & Intelligent Extraction ---")
    
    try:
        # 2. Scrape Page
        raw_text = await scraper.get_page_content(target_url)
        
        # 3. Parse Data
        job_data = await scraper.parse_job_details(raw_text)
        
        logger.info(f"Target Identified: {job_data.get('Job Title')} at {job_data.get('Company Name')}")

        logger.info("--- Starting Phase 3: The Markdown Tailor ---")
        
        # 4. Load and Tailor CV
        base_cv = tailor.load_base_cv()
        tailored_markdown = await tailor.tailor_cv(base_cv, job_data)
        
        # 5. Generate PDF
        # Clean filename logic
        company_name = job_data.get('Company Name') or 'Company'
        safe_company = "".join(x for x in company_name if x.isalnum())
        pdf_filename = f"CV_{safe_company}.pdf"
        
        pdf_path = tailor.generate_pdf(tailored_markdown, pdf_filename)

        logger.info("--- Starting Phase 4: Execution & Upload Stub ---")
        
        if pdf_path:
            # 6. Upload Application
            submitter = ApplicationSubmitter()
            await submitter.submit_application(target_url, pdf_path)
        else:
            logger.error("[!] Could not proceed to upload due to PDF generation failure.")
            
    except JobHunterError as e:
        logger.error(f"Job Hunter Bot failed: {e}")
    except Exception as e:
        logger.exception(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    asyncio.run(main())