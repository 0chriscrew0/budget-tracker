from pydantic import BaseModel
from datetime import datetime, date


class ExpenseIn(BaseModel):
    label: str
    amount: float
    date: date

class ExpenseOut(ExpenseIn):
    id: str
    budget_id: str
    created_at: datetime
