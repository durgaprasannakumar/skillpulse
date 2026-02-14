import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    ADZUNA_APP_ID = os.getenv("ADZUNA_APP_ID")
    ADZUNA_APP_KEY = os.getenv("ADZUNA_APP_KEY")
    ADZUNA_COUNTRY = "us"

    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY")

    DB_PATH = "skillpulse.db"
    MAX_RESULTS = 100
