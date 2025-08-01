from pydantic import BaseModel
from datetime import datetime

from models.expense import ExpenseOut

class BudgetIn(BaseModel):
    name: str
    amount: float
    month: str

class BudgetOut(BudgetIn):
    id: str
    created_at: datetime
    balance: float

class BudgetDetail(BaseModel):
    id: str
    name: str
    amount: float
    month: str
    balance: float
    expenses: list[ExpenseOut]

