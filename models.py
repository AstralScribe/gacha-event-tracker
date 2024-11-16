from pydantic import BaseModel
from typing import Literal, Optional
import datetime

class GameEvents(BaseModel):
    game_name: str
    event_name: str
    is_completed: bool = False
    game_type: Literal["long", "short"]
    end_date: Optional[datetime.date] = None
    time_left: Optional[int] = None


class UpdateData(BaseModel):
    id: int
    is_completed: bool