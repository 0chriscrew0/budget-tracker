from pydantic import BaseModel
from datetime import datetime

class BudgetIn(BaseModel):
    name: str
    amount: float
    month: str

class BudgetOut(BudgetIn):
    id: str
    created_at: datetime
    balance: float
