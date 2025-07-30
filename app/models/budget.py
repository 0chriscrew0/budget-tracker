from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class BudgetIn(BaseModel):
    name: str
    amount: float
    month: str  # format: "2025-07"
    created_by: Optional[str] = None  # you can hook this up to auth later

class BudgetOut(BudgetIn):
    id: str
    created_at: datetime
