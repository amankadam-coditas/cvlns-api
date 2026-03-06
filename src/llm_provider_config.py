# from app.config import settings
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.openai import OpenAIProvider
from src.config import settings

# configure OpenAI provider; key can also be pulled from settings or env
provider = OpenAIProvider(
    base_url=settings.BASE_URL,
    api_key=settings.API_KEY,
)

model = OpenAIChatModel(
    "gpt-4o",  # or any other OpenAI model name
    provider=provider,
)
