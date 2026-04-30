from dotenv import load_dotenv
import os

load_dotenv()

class Settings:
    DATABASE_URL : str | None = os.getenv("DATABASE_URL")
    # SECRET_KEY = os.getenv("SECRET_KEY")
    # DEBUG: bool = os.getenv("DEBUG") == "true"
    
    def get_database_url(self):
        if not self.DATABASE_URL:
            raise ValueError("DATABASE_URL is not set in environment variables")
        return self.DATABASE_URL
        

settings = Settings()