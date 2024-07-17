from fastapi import Depends, HTTPException, status
from app.config import get_settings, Settings
from app.agents.caddie_agent import CaddieAgent
from app.agents.coach_agent import CoachAgent
from app.agents.skill_agent import SkillAgent
from app.models.agent_config import AgentConfig
from app.models.user_input import UserInput
from app.models.base import AgentType


from collections.abc import Generator
from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError
from pydantic import ValidationError
from sqlmodel import Session

from app.core import security
from app.core.config import settings
from app.core.db import engine
from app.models import TokenPayload, User

reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/login/access-token"
)


def get_db() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_db)]
TokenDep = Annotated[str, Depends(reusable_oauth2)]


def get_current_user(session: SessionDep, token: TokenDep) -> User:
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[security.ALGORITHM]
        )
        token_data = TokenPayload(**payload)
    except (InvalidTokenError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )
    user = session.get(User, token_data.sub)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]


def get_current_active_superuser(current_user: CurrentUser) -> User:
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=403, detail="The user doesn't have enough privileges"
        )
    return current_user

async def get_agent(agent_type: AgentType, settings: Settings = Depends(get_settings)):
    agent_config = AgentConfig(
        agent_type=agent_type,
        openai_api_key=settings.OPENAI_API_KEY,
        groq_api_key=settings.GROQ_API_KEY,
        user_context="Golf assistant"
    )
    if agent_type == AgentType.CADDIE:
        return CaddieAgent(config=agent_config)
    elif agent_type == AgentType.COACH:
        return CoachAgent(config=agent_config)
    elif agent_type == AgentType.SKILL:
        return SkillAgent(config=agent_config)
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid agent type")

async def validate_user_input(user_input: UserInput) -> UserInput:
    if user_input.input_type == "file" and not user_input.file_path:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="File path is required for file input type")
    return user_input