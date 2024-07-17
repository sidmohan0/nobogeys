from abc import ABC, abstractmethod
from app.models.agent_config import AgentConfig
from app.models.agent_communication import AgentRequest, AgentResponse

class BaseAgent(ABC):
    def __init__(self, config: AgentConfig):
        self.config = config

    @abstractmethod
    async def process_request(self, request: AgentRequest) -> AgentResponse:
        pass