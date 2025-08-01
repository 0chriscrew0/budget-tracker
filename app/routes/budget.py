from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException
from models.expense import ExpenseIn, ExpenseOut
from models.budget import BudgetDetail, BudgetIn, BudgetOut
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

    expense_sums = await db.expenses.aggregate([
        {"$match": {"user_id": str(user["_id"])}},
        {"$group": {
            "_id": "$budget_id",
            "total": {"$sum": "$amount"}
        }}
    ]).to_list(length=100)

    expense_totals = {item["_id"]: item["total"] for item in expense_sums}

    budgets = [
        BudgetOut(
            id=str(doc["_id"]),
            name=doc["name"],
            amount=doc["amount"],
            month=doc["month"],
            created_at=doc["created_at"],
            balance=doc["amount"] - expense_totals.get(str(doc["_id"]), 0)
        )
        for doc in budget_docs
    ]

    return budgets

@router.get("/budgets/{budget_id}", response_model=BudgetDetail)
async def get_budget(budget_id: str, user: dict = Depends(get_current_user)):
    budget = await db.budgets.find_one({
        "_id": ObjectId(budget_id),
        "user_id": str(user["_id"])
    })
    if budget is None:
        raise HTTPException(404, "Budget not found.")
    
    expenses = await db.expenses.find({
        "budget_id": str(budget["_id"]),
        "user_id": str(user["_id"])
    }).to_list(length=100)

    total_spent = sum(expense["amount"] for expense in expenses)
    balance = budget["amount"] - total_spent

    expenses_out = [
        ExpenseOut(
            id=str(exp["_id"]),
            label=exp["label"],
            amount=exp["amount"],
            date=exp.get("date"),  # include if using
            budget_id=exp["budget_id"],
            created_at=exp["created_at"]
        )
        for exp in expenses
    ]

    return BudgetDetail(
        id=str(budget["_id"]),
        name=budget["name"],
        amount=budget["amount"],
        month=budget["month"],
        balance=balance,
        expenses=expenses_out
    )



@router.post("/budgets/{budget_id}/expenses", response_model=ExpenseOut)
async def create_expense(expense: ExpenseIn, budget_id: str, user: dict = Depends(get_current_user)):
    budget = await db.budgets.find_one({
        "_id": ObjectId(budget_id),
        "user_id": str(user["_id"])
    })
    if budget is None:
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

