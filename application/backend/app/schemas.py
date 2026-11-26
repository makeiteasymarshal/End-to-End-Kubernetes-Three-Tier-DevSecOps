"""Pydantic schemas for request and response validation."""

from datetime import datetime
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


class TaskStatus(str, Enum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


class TaskPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class TaskCreate(BaseModel):
    title: str = Field(..., min_length=2, max_length=120)
    description: Optional[str] = Field(default="", max_length=500)
    status: TaskStatus = Field(default=TaskStatus.OPEN)
    priority: TaskPriority = Field(default=TaskPriority.MEDIUM)
    owner: str = Field(default="platform-team", min_length=2, max_length=60)


class TaskUpdate(BaseModel):
    title: Optional[str] = Field(default=None, min_length=2, max_length=120)
    description: Optional[str] = Field(default=None, max_length=500)
    status: Optional[TaskStatus] = None
    priority: Optional[TaskPriority] = None
    owner: Optional[str] = Field(default=None, min_length=2, max_length=60)


class TaskResponse(BaseModel):
    id: int
    title: str
    description: str
    status: TaskStatus
    priority: TaskPriority
    owner: str
    created_at: datetime
    updated_at: datetime


class HealthResponse(BaseModel):
    status: str
    environment: str
    database: Optional[str] = None
    version: str
