import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """
    Central configuration class.
    Ensures all environment variables are loaded and accessible.
    """
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    
    # Path to your local Chrome User Data directory (Critical for Session Persistence)
    # Example Windows: C:\\Users\\Name\\AppData\\Local\\Google\\Chrome\\User Data
    # Example Linux: /home/user/.config/google-chrome
    CHROME_USER_DATA_DIR = os.getenv("CHROME_USER_DATA_DIR", "/home/erick/.config/google-chrome")
    
    # The specific profile folder (usually "Default" or "Profile 1")
    CHROME_PROFILE_DIR = os.getenv("CHROME_PROFILE_DIR", "Default")
    
    # Path to wkhtmltopdf binary (if not in system PATH)
    WKHTMLTOPDF_PATH = os.getenv("WKHTMLTOPDF_PATH", "")

    # Paths for files
    BASE_CV_PATH = "base_cv.md"
    OUTPUT_DIR = "generated_cvs"
    AUTH_FILE_PATH = "auth.json"

    @staticmethod
    def validate():
        if not Config.OPENAI_API_KEY:
            raise ValueError("Missing OPENAI_API_KEY in .env")
        if not Config.CHROME_USER_DATA_DIR:
            raise ValueError("Missing CHROME_USER_DATA_DIR in .env")