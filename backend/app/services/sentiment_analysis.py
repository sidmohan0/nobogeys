from app.models.nlp_tags import SentimentTag
from app.models.base import AgentType
from app.config import get_settings
from groq import Groq
from openai import OpenAI
import instructor
from pydantic import BaseModel, Field
from app.config import get_settings, SentimentAnalysis

# load settings
settings = get_settings()

def initialize_groq():
    return Groq(api_key=settings.GROQ_API_KEY)

def initialize_openai():
    return instructor.patch(OpenAI(api_key=settings.OPENAI_API_KEY))

class SentimentAnalysis(BaseModel):
    sentiment: SentimentTag = Field(..., description="The overall sentiment of the text")
    confidence: float = Field(..., ge=0, le=1, description="Confidence score of the sentiment analysis")
    explanation: str = Field(..., max_length=500, description="Brief explanation of the sentiment analysis")



def analyze_sentiment(text: str, use_groq: bool = True) -> SentimentAnalysis:
    config = settings.sentiment_analysis
    prompt = config.prompt_template.format(text=text)
    
    messages = [
        {"role": "system", "content": config.system_message},
        {"role": "user", "content": prompt}
    ]
    
    common_params = {
        "messages": messages,
        "temperature": config.temperature,
        "max_tokens": config.max_tokens,
        "response_model": SentimentAnalysis
    }
    
    if use_groq:
        client = initialize_groq()
        response = client.chat.completions.create(
            model=config.groq_model,
            **common_params
        )
    else:
        client = initialize_openai()
        response = client.chat.completions.create(
            model=config.openai_model,
            **common_params
        )
    
    return response
