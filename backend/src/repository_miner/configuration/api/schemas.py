from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field, HttpUrl


class ConfigurationUpdateDto(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str | None = Field(default=None, min_length=1, max_length=120)
    timezone: str | None = None
    enabled: bool | None = None


class ConfigurationSelectionDto(BaseModel):
    kind: str
    mode: str
    external_id: str


class ConfigurationScheduleDto(BaseModel):
    recurrence: str
    local_time: str
    weekday: int | None = None
    day_of_month: int | None = None
    timezone: str
    next_run_at: str | None = None


class ConfigurationDetailDto(BaseModel):
    id: str
    name: str
    gitlab_base_url: HttpUrl
    timezone: str
    enabled: bool
    target_branch: str | None
    credential_status: str
    connection_validated: bool
    allowed_emails: list[str]
    selections: list[ConfigurationSelectionDto]
    schedule: ConfigurationScheduleDto | None


class ManualExecutionStartedDto(BaseModel):
    execution_id: str
    status: str
