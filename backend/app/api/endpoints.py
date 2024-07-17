from fastapi import APIRouter, Depends, HTTPException, status
from app.models.user_input import UserInput
from app.models.agent_communication import AgentRequest, AgentResponse
from app.agents.base_agent import BaseAgent
from app.models.base import AgentType
from .dependencies import get_agent, validate_user_input
from app.services.agent_type_analysis import analyze_agent_types
from app.services.sentiment_analysis import analyze_sentiment
from app.api.routes import items, login, users, utils


api_router = APIRouter()
api_router.include_router(login.router, tags=["login"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(utils.router, prefix="/utils", tags=["utils"])
api_router.include_router(items.router, prefix="/items", tags=["items"])

@api_router.post("/analyze", response_model=list[AgentResponse])
async def analyze_golf_situation(
    user_input: UserInput = Depends(validate_user_input),
    caddie_agent: BaseAgent = Depends(lambda: get_agent(AgentType.CADDIE))
):
    try:
        agent_request = AgentRequest(user_input=user_input, agent_config=caddie_agent.config)
        responses = await caddie_agent.process_request(agent_request)
        return responses
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@api_router.post("/agent_type_analysis")
async def perform_agent_type_analysis(user_input: UserInput = Depends(validate_user_input)):
    try:
        analysis = await analyze_agent_types(user_input)
        return analysis
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@api_router.post("/sentiment_analysis")
async def perform_sentiment_analysis(user_input: UserInput = Depends(validate_user_input)):
    try:
        sentiment = await analyze_sentiment(user_input.content)
        return sentiment
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@api_router.get("/health")
async def health_check():
    return {"status": "healthy"}
