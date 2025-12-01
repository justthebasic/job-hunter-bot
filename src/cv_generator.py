import os
import markdown2
import pdfkit
from openai import AsyncOpenAI
from config import Config
from src.logger import setup_logger
from src.exceptions import PDFGenerationError

logger = setup_logger(__name__)

class CVTailor:
    """
    Handles CV customization and PDF generation.
    """
    
    def __init__(self):
        self.openai_client = AsyncOpenAI(api_key=Config.OPENAI_API_KEY)
        
        # Configure pdfkit with path to wkhtmltopdf if necessary
        self.pdf_config = None
        if Config.WKHTMLTOPDF_PATH:
            self.pdf_config = pdfkit.configuration(wkhtmltopdf=Config.WKHTMLTOPDF_PATH)

    def load_base_cv(self) -> str:
        """Reads the local master CV markdown file."""
        if not os.path.exists(Config.BASE_CV_PATH):
            raise FileNotFoundError(f"Base CV not found at {Config.BASE_CV_PATH}")
        
        with open(Config.BASE_CV_PATH, 'r', encoding='utf-8') as f:
            return f.read()

    async def tailor_cv(self, base_cv: str, job_data: dict) -> str:
        """
        Uses LLM to rewrite the Summary and reorder Skills based on job data.
        """
        logger.info(f"[*] Tailoring CV for {job_data.get('Job Title', 'Job')}...")
        
        prompt = (
            f"Role: You are an expert Resume Writer specializing in ATS (Applicant Tracking Systems) optimization.\n"
            f"Task: Adapt the provided Base CV for this specific Job Description to maximize the match score.\n\n"
            f"--- GUIDELINES ---\n"
            f"1. **Header**: PRESERVE the Name and Contact Information (Email, Phone, LinkedIn, etc.) exactly as they appear in the Base CV at the very top. Preserve the exact formatting of the header.\n"
            f"2. **Professional Summary**: Rewrite to align perfectly with the job's core requirements. Use keywords from the job description naturally.\n"
            f"3. **Skills**: Reorder and filter skills. Prioritize the top 10-15 most relevant 'Hard Skills' mentioned in the job data. Ensure exact keyword matching.\n"
            f"4. **Experience**: Keep the history but tweak bullet points to emphasize achievements relevant to this role. For each role, rewrite max 3-5 bullet points focused on the most relevant accomplishments. Use strong action verbs (e.g., 'Orchestrated', 'Developed', 'Optimized').\n"
            f"5. **Formatting**: Use standard Markdown headers. Strict Order: # Name, ## Professional Summary, ## Skills, ## Experience, ## Education. Do not use columns or complex tables.\n"
            f"6. **Output**: Return STRICTLY the Markdown content. No conversational filler.\n\n"
            f"--- JOB DATA ---\n{job_data}\n\n"
            f"--- BASE CV ---\n{base_cv}"
        )

        try:
            response = await self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"[!] CV Tailoring error: {e}")
            return base_cv # Return original on failure

    def generate_pdf(self, markdown_content: str, filename: str):
        """
        Converts Markdown -> HTML -> PDF.
        """
        logger.info(f"[*] Generating PDF: {filename}...")
        
        # Ensure output directory exists
        os.makedirs(Config.OUTPUT_DIR, exist_ok=True)
        output_path = os.path.join(Config.OUTPUT_DIR, filename)

        # Load CSS
        css_content = ""
        css_path = os.path.join("assets", "style.css")
        if os.path.exists(css_path):
            with open(css_path, 'r', encoding='utf-8') as f:
                css_content = f.read()
        else:
            logger.warning(f"CSS file not found at {css_path}. Using default styles.")

        # Convert MD to HTML with basic styling
        html_content = markdown2.markdown(markdown_content)
        
        # Add basic CSS for clean PDF rendering
        styled_html = f"""
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                {css_content}
            </style>
        </head>
        <body>
            {html_content}
        </body>
        </html>
        """

        try:
            pdfkit.from_string(
                styled_html, 
                output_path, 
                configuration=self.pdf_config,
                options={"encoding": "UTF-8"}
            )
            logger.info(f"[*] PDF saved successfully at: {output_path}")
            return output_path
        except Exception as e:
            logger.error(f"[!] PDF Generation error: {e}")
            raise PDFGenerationError(f"Failed to generate PDF: {e}")