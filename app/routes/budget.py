from fastapi import APIRouter, HTTPException
from models.budget import BudgetIn, BudgetOut
from config import db
from bson import ObjectId
from datetime import datetime

router = APIRouter()

@router.post("/budgets", response_model=BudgetOut)
async def create_budget(budget: BudgetIn):
    data = budget.dict()
    data["created_at"] = datetime.utcnow()
    
    result = await db.budgets.insert_one(data)
    new_budget = await db.budgets.find_one({"_id": result.inserted_id})

    return BudgetOut(
        id=str(new_budget["_id"]),
        name=new_budget["name"],
        amount=new_budget["amount"],
        month=new_budget["month"],
        created_by=new_budget.get("created_by"),
        created_at=new_budget["created_at"]
    )

@router.get("/budgets", response_model=list[BudgetOut])
async def get_budgets():
    budgets_cursor = db.budgets.find()
    budgets = []
    async for doc in budgets_cursor:
        budgets.append(BudgetOut(
            id=str(doc["_id"]),
            name=doc["name"],
            amount=doc["amount"],
            month=doc["month"],
            created_by=doc.get("created_by"),
            created_at=doc["created_at"]
        ))
    return budgets
