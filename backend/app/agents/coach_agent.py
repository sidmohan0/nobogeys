from .base_agent import BaseAgent
from app.models.agent_communication import AgentRequest, AgentResponse
from app.models.agent_config import AgentConfig
from app.models.user_input import UserInput
from app.utils.helpers import sanitize_input, format_agent_response, calculate_sentiment_score, extract_key_entities, is_valid_golf_input

class CoachAgent(BaseAgent):
    def __init__(self, config: AgentConfig):
        super().__init__(config)

    async def get_player_notes(self, user_input: UserInput) -> str:
        # Implementation
        return "Player notes"

    async def get_player_tips(self, user_input: UserInput) -> str:
        # Implementation
        return "Player tips"

    async def process_request(self, request: AgentRequest) -> AgentResponse:
        # Implement the logic to process the request
        # This method should use get_player_notes and get_player_tips as needed
        sanitized_input = sanitize_input(request.user_input.content)
        if not is_valid_golf_input(sanitized_input):
            return AgentResponse(agent_type=self.config.agent_type, result="Invalid golf input")
        
        notes = await self.get_player_notes(request.user_input)
        tips = await self.get_player_tips(request.user_input)
        
        result = format_agent_response({"notes": notes, "tips": tips})
        return AgentResponse(agent_type=self.config.agent_type, result=result)