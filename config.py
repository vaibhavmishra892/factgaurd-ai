import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Configuration class for API keys and settings"""
    
    # Cerebras API Configuration (using Llama 3.1 8B model)
    CEREBRAS_API_KEY = os.getenv("CEREBRAS_API_KEY", "")
    LLM_MODEL = os.getenv("LLM_MODEL", "llama3.1-8b")  # Cerebras official: llama3.1-8b
    LLM_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", "0.3"))
    CEREBRAS_BASE_URL = os.getenv("CEREBRAS_BASE_URL", "https://api.cerebras.ai/v1")
    
    # API Keys (for data sources)
    ALPHA_VANTAGE_KEY = os.getenv("ALPHA_VANTAGE_KEY", "")
    NEWS_API_KEY = os.getenv("NEWS_API_KEY", "")
    SERP_API_KEY = os.getenv("SERP_API_KEY", "")
    
    # API Endpoints
    ALPHA_VANTAGE_BASE_URL = "https://www.alphavantage.co/query"
    NEWS_API_BASE_URL = "https://newsapi.org/v2/everything"
    SERP_API_BASE_URL = "https://serpapi.com/search"
    
    # Currency Configuration
    USD_TO_INR_RATE = 83.5  # Approximate conversion rate (update as needed)
    PRIMARY_CURRENCY = "INR"
    
    # Confidence Thresholds
    HIGH_CONFIDENCE_THRESHOLD = 0.8
    MEDIUM_CONFIDENCE_THRESHOLD = 0.5
    
    @classmethod
    def validate(cls):
        """Validate that required API keys are present"""
        missing_keys = []
        
        if not cls.CEREBRAS_API_KEY:
            missing_keys.append("CEREBRAS_API_KEY")
        if not cls.ALPHA_VANTAGE_KEY:
            missing_keys.append("ALPHA_VANTAGE_KEY")
        if not cls.NEWS_API_KEY:
            missing_keys.append("NEWS_API_KEY")
        if not cls.SERP_API_KEY:
            missing_keys.append("SERP_API_KEY")
        
        if missing_keys:
            print(f"⚠️  Warning: Missing API keys: {', '.join(missing_keys)}")
            print("   Please add them to your .env file.")
        
        print(f"🤖 Using Cerebras API with model: {cls.LLM_MODEL}")
        
        return len(missing_keys) == 0

# Create instance
config = Config()
