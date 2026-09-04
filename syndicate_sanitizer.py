import re
from pydantic import BaseModel, Field, field_validator

class MatchQueueItem(BaseModel):
    match_id: str = Field(..., description="Unique match identifier")
    tournament: str = Field(..., description="Tournament or series name")
    match_name: str = Field(..., description="Team A vs Team B string")
    date: str = Field(..., description="Match date YYYY-MM-DD")

    @field_validator('match_id')
    @classmethod
    def validate_match_id(cls, v: str) -> str:
        if not re.fullmatch(r'\d+', v):
            raise ValueError("Match ID must contain only digits.")
        return v

    @field_validator('match_name')
    @classmethod
    def validate_match_name(cls, v: str) -> str:
        if " vs " not in v:
            raise ValueError("Match name must follow 'Team A vs Team B' syntax.")
        return v

class ParsedPlayer(BaseModel):
    name: str = Field(..., max_length=50)
    role: str = Field(..., pattern=r'^(WK|BAT|AR|BOWL)$')
    team: str
    is_playing: bool

    @field_validator('name')
    @classmethod
    def sanitize_name(cls, v: str) -> str:
        clean_val = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', v)
        return clean_val.strip()
