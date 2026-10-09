from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import models, schemas
from app.db import get_db
from app.services import ai_client

router = APIRouter(tags=["codegen"])


@router.post("/test-cases/{test_case_id}/generate-script", response_model=schemas.PlaywrightScriptOut)
def generate_script(test_case_id: int, db: Session = Depends(get_db)):
    test_case = db.get(models.TestCase, test_case_id)
    if not test_case:
        raise HTTPException(404, "Test case not found")
    if test_case.status != "approved":
        raise HTTPException(400, "Test case must be approved before generating a Playwright script")

    customer = db.get(models.Customer, test_case.customer_id)
    documents = (
        db.query(models.Document).filter(models.Document.customer_id == customer.id).all()
    )

    code = ai_client.generate_playwright_code(customer, documents, test_case)

    script = test_case.script
    if script is None:
        script = models.PlaywrightScript(test_case_id=test_case_id, code=code)
        db.add(script)
    else:
        script.code = code
    db.commit()
    db.refresh(script)
    return script


@router.get("/test-cases/{test_case_id}/script", response_model=schemas.PlaywrightScriptOut)
def get_script(test_case_id: int, db: Session = Depends(get_db)):
    test_case = db.get(models.TestCase, test_case_id)
    if not test_case or not test_case.script:
        raise HTTPException(404, "No script generated yet")
    return test_case.script
