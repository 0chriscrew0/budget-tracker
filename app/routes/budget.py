from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException
from models.expense import ExpenseIn, ExpenseOut
from models.budget import BudgetIn, BudgetOut
from auth.utils import get_current_user
from config import db
from datetime import datetime, timezone

router = APIRouter()

@router.post("/budgets", response_model=BudgetOut)
async def create_budget(budget: BudgetIn, user: dict = Depends(get_current_user)):
    data = budget.model_dump()
    data["user_id"] = str(user["_id"])
    data["created_at"] = datetime.now(timezone.utc)
    
    result = await db.budgets.insert_one(data)
    new_budget = await db.budgets.find_one({"_id": result.inserted_id})

    return BudgetOut(
        id=str(new_budget["_id"]),
        name=new_budget["name"],
        amount=new_budget["amount"],
        month=new_budget["month"],
        created_at=new_budget["created_at"]
    )

@router.get("/budgets", response_model=list[BudgetOut])
async def get_budgets(user: dict = Depends(get_current_user)):
    budgets_cursor = db.budgets.find({"user_id": str(user["_id"])})
    budget_docs = await budgets_cursor.to_list(length=100)

    budgets = [
        BudgetOut(
            id=str(doc["_id"]),
            name=doc["name"],
            amount=doc["amount"],
            month=doc["month"],
            created_at=doc["created_at"]
        )
        for doc in budget_docs
    ]

    return budgets

@router.post("/budgets/{budget_id}/expenses", response_model=ExpenseOut)
async def create_expense(expense: ExpenseIn, budget_id: str, user: dict = Depends(get_current_user)):
    budget = await db.budgets.find_one({
        "_id": ObjectId(budget_id),
        "user_id": str(user["_id"])
    })
    if budget == None:
        raise HTTPException(404, "Budget not found.")
    
    data = expense.model_dump()
    data["budget_id"] = str(budget["_id"])
    data["user_id"] = str(user["_id"])
    data["created_at"] = datetime.now(timezone.utc)
    data["date"] = datetime.combine(data["date"], datetime.min.time())

    result = await db.expenses.insert_one(data)
    new_expense = await db.expenses.find_one({"_id": result.inserted_id})

    return ExpenseOut(
        id=str(new_expense["_id"]),
        label=new_expense["label"],
        amount=new_expense["amount"],
        date=new_expense["date"],
        budget_id=new_expense["budget_id"],
        created_at=new_expense["created_at"]
    )
    
@router.get("/protected")
async def protected_route(user: dict = Depends(get_current_user)):
    return {"message": f"Welcome, {user['username']}!"}

