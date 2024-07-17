from pydantic import EmailStr
from sqlmodel import Field, Relationship, SQLModel


# Shared properties
class UserBase(SQLModel):
    email: EmailStr = Field(unique=True, index=True, max_length=255)
    is_active: bool = True
    is_superuser: bool = False
    full_name: str | None = Field(default=None, max_length=255)


# Properties to receive via API on creation
class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=40)


class UserRegister(SQLModel):
    email: EmailStr = Field(max_length=255)
    password: str = Field(min_length=8, max_length=40)
    full_name: str | None = Field(default=None, max_length=255)


# Properties to receive via API on update, all are optional
class UserUpdate(UserBase):
    email: EmailStr | None = Field(default=None, max_length=255)  # type: ignore
    password: str | None = Field(default=None, min_length=8, max_length=40)


class UserUpdateMe(SQLModel):
    full_name: str | None = Field(default=None, max_length=255)
    email: EmailStr | None = Field(default=None, max_length=255)


class UpdatePassword(SQLModel):
    current_password: str = Field(min_length=8, max_length=40)
    new_password: str = Field(min_length=8, max_length=40)


# Database model, database table inferred from class name
class User(UserBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    hashed_password: str
    items: list["Item"] = Relationship(back_populates="owner")


# Properties to return via API, id is always required
class UserPublic(UserBase):
    id: int


class UsersPublic(SQLModel):
    data: list[UserPublic]
    count: int


# Shared properties
class ItemBase(SQLModel):
    title: str = Field(min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=255)


# Properties to receive on item creation
class ItemCreate(ItemBase):
    title: str = Field(min_length=1, max_length=255)


# Properties to receive on item update
class ItemUpdate(ItemBase):
    title: str | None = Field(default=None, min_length=1, max_length=255)  # type: ignore


# Database model, database table inferred from class name
class Item(ItemBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    title: str = Field(max_length=255)
    owner_id: int | None = Field(default=None, foreign_key="user.id", nullable=False)
    owner: User | None = Relationship(back_populates="items")


# Properties to return via API, id is always required
class ItemPublic(ItemBase):
    id: int
    owner_id: int


class ItemsPublic(SQLModel):
    data: list[ItemPublic]
    count: int


# Generic message
class Message(SQLModel):
    message: str


# JSON payload containing access token
class Token(SQLModel):
    access_token: str
    token_type: str = "bearer"


# Contents of JWT token
class TokenPayload(SQLModel):
    sub: int | None = None


class NewPassword(SQLModel):
    token: str
    new_password: str = Field(min_length=8, max_length=40)

from pydantic import BaseModel
from typing import Optional
from app.models.user_input import UserInput
from app.models.agent_config import AgentConfig
from app.models.base import AgentType
from app.config import SentimentAnalysis, AgentTypeAnalysis

class AgentRequest(BaseModel):
    user_input: UserInput
    agent_config: AgentConfig
    sentiment_analysis: Optional[SentimentAnalysis] = None
    agent_type_analysis: Optional[AgentTypeAnalysis] = None

class AgentResponse(BaseModel):
    agent_type: AgentType
    result: str
    metadata: Optional[dict] = None

from pydantic import BaseModel
from typing import Optional
from .base import AgentType
from app.config import get_settings

class AgentConfig(BaseModel):
    agent_type: AgentType
    user_context: str
    config_path: Optional[str] = None

    @property
    def openai_api_key(self):
        return get_settings().OPENAI_API_KEY

    @property
    def groq_api_key(self):
        return get_settings().GROQ_API_KEY
    
from enum import Enum


class AgentType(str, Enum):
    CADDIE = "CaddieAgent"
    SKILL = "SkillAgent"
    COACH = "CoachAgent"
    COURSE = "CourseAgent"
    DATA = "DataAgent"

from enum import Enum

class NLPTag(Enum):
    def __str__(self):
        return self.value

class SentimentTag(NLPTag):
    POSITIVE = "positive"
    NEUTRAL = "neutral"
    NEGATIVE = "negative"

from pydantic import BaseModel
from typing import Optional
from app.models.base import InputType
from enum import Enum


class UserInput(BaseModel):
    input_type: InputType
    content: str
    file_path: Optional[str] = None

class InputType(str, Enum):
    FILE = "file"
    TEXT = "text"
    IMAGE = "image"
    AUDIO = "audio"
