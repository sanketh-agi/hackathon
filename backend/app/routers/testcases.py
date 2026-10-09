from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import models, schemas
from app.db import get_db
from app.services import ai_client

router = APIRouter(tags=["test-cases"])


@router.post("/customers/{customer_id}/test-cases/generate", response_model=list[schemas.TestCaseOut])
def generate_test_cases(customer_id: int, payload: schemas.GenerateRequest, db: Session = Depends(get_db)):
    customer = db.get(models.Customer, customer_id)
    if not customer:
        raise HTTPException(404, "Customer not found")
    rule = db.get(models.Rule, payload.rule_id)
    if not rule or rule.customer_id != customer_id:
        raise HTTPException(404, "Rule not found for this customer")

    generated = ai_client.generate_test_cases(
        customer, rule, instructions=payload.instructions, count_hint=payload.count_hint
    )

    rows = []
    for tc in generated:
        row = models.TestCase(
            customer_id=customer_id,
            rule_id=rule.id,
            title=tc["title"],
            preconditions=tc["preconditions"],
            steps_json=tc["steps"],
            expected_result=tc["expected_result"],
            priority=tc["priority"],
            requirement_trace=tc["requirement_trace"],
            status="draft",
        )
        db.add(row)
        rows.append(row)
    db.commit()
    for row in rows:
        db.refresh(row)
    return rows


@router.get("/customers/{customer_id}/test-cases", response_model=list[schemas.TestCaseOut])
def list_test_cases(customer_id: int, db: Session = Depends(get_db)):
    return (
        db.query(models.TestCase)
        .filter(models.TestCase.customer_id == customer_id)
        .order_by(models.TestCase.id.desc())
        .all()
    )


@router.patch("/test-cases/{test_case_id}", response_model=schemas.TestCaseOut)
def update_test_case(test_case_id: int, payload: schemas.TestCaseUpdate, db: Session = Depends(get_db)):
    test_case = db.get(models.TestCase, test_case_id)
    if not test_case:
        raise HTTPException(404, "Test case not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(test_case, field, value)
    db.commit()
    db.refresh(test_case)
    return test_case


@router.post("/test-cases/{test_case_id}/approve", response_model=schemas.TestCaseOut)
def approve_test_case(test_case_id: int, db: Session = Depends(get_db)):
    test_case = db.get(models.TestCase, test_case_id)
    if not test_case:
        raise HTTPException(404, "Test case not found")
    test_case.status = "approved"
    test_case.approved_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(test_case)
    return test_case
