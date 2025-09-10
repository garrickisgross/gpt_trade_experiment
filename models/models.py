from pydantic import BaseModel, Field
from uuid import UUID, uuid4
from typing import Any, Annotated, Union, Literal, List, Dict
from datetime import datetime

class Base(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    name: str

class Position(Base):
    kind: Literal["position"] = "position"
    symbol: str
    status: str
    qty: int
    avg_price: float
    stop_loss: float
    thesis: List[str] = []
    strategy_id: UUID

class Strategy(Base):
    kind: Literal["strategy"] = "strategy"
    goal: str
    capital: float
    universe: str
    risk_params: Dict[str, Any] = {}
    benchmark: List[str] = []
    positions: Dict[str, Position] = {}

Model_Type = Annotated[Union[Strategy, Position], Field(discriminator="kind")]