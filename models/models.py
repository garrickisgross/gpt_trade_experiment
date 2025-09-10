from pydantic import BaseModel, Field, ConfigDict, field_serializer, field_validator
from uuid import UUID, uuid4
from typing import Any, Annotated, Union, Literal, List, Dict
import pandas as pd
import io

class Base(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    name: str

class Position(Base):
    kind: Literal["position"] = "position"
    status: str
    qty: int
    avg_price: float
    stop_loss: float
    target: float
    thesis: List[str] = []
    strategy_name: str 

class Strategy(Base):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    kind: Literal["strategy"] = "strategy"
    goal: str
    capital: float
    universe: str
    risk_params: Dict[str, Any] = {}
    benchmark: List[str] = []
    positions: List[Position] = []
    position_history: pd.DataFrame = Field(default_factory=pd.DataFrame)

    @field_serializer("position_history", when_used="json")
    def _dump_df(self, df: pd.DataFrame, _info):
        if df is None or df.empty:
            return []
        return df.to_csv(index=False)
    
    @field_validator("position_history", mode="before")
    @classmethod
    def _coerce_df(cls, v):
        if v is None or isinstance(v, pd.DataFrame):
            return v
        
        if isinstance(v, list) or isinstance(v, dict):
            return pd.DataFrame(v)
        
        if isinstance(v, str):
            try:
                return pd.read_csv(io.StringIO(v))
            except:
                pass

        raise TypeError("Unsupported format for history.")
    

    



Model_Type = Annotated[Union[Strategy, Position], Field(discriminator="kind")]