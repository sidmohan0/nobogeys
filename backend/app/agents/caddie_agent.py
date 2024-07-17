from .base_agent import BaseAgent
from app.models.agent_communication import AgentRequest, AgentResponse
from app.services.sentiment_analysis import analyze_sentiment
from app.services.agent_type_analysis import analyze_agent_types
from app.models.agent_config import AgentConfig
from app.models.user_input import UserInput

class CaddieAgent(BaseAgent):
    def __init__(self, config: AgentConfig):
        super().__init__(config)

    async def process_request(self, request: AgentRequest) -> list[AgentResponse]:
        sentiment_result = await self.run_sentiment_analysis(request.user_input.content)
        agent_type_result = await self.run_agent_type_analysis(request.user_input)

        return [AgentResponse(...)]  # Return list of AgentResponse objects