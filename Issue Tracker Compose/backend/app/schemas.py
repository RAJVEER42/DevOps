from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

Status = Literal["open", "in_progress", "done"]
Priority = Literal["low", "medium", "high"]


class IssueIn(BaseModel):
    title: str = Field(min_length=1, max_length=120)
    description: str = ""
    status: Status = "open"
    priority: Priority = "medium"
    assignee: str = Field(default="", max_length=60)


class IssueUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=120)
    description: str | None = None
    status: Status | None = None
    priority: Priority | None = None
    assignee: str | None = Field(default=None, max_length=60)


class IssueOut(IssueIn):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class Stats(BaseModel):
    total: int
    by_status: dict[str, int]
    by_priority: dict[str, int]
    open_high_priority: int
