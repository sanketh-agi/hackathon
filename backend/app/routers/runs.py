from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import models, schemas
from app.db import get_db
from app.services import playwright_runner

router = APIRouter(tags=["runs"])


@router.post("/test-cases/{test_case_id}/run", response_model=schemas.TestRunOut)
def run_test_case(test_case_id: int, db: Session = Depends(get_db)):
    test_case = db.get(models.TestCase, test_case_id)
    if not test_case:
        raise HTTPException(404, "Test case not found")
    if not test_case.script:
        raise HTTPException(400, "Generate a Playwright script for this test case first")

    customer = db.get(models.Customer, test_case.customer_id)

    run = models.TestRun(test_case_id=test_case_id, status="running")
    db.add(run)
    db.commit()
    db.refresh(run)

    spec_path = playwright_runner.write_spec(test_case_id, test_case.script.code)
    report = playwright_runner.run_spec(spec_path, customer.app_url)

    run.status = "passed" if report.get("_returncode") == 0 else "failed"
    run.result_json = report
    run.finished_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(run)
    return run


@router.get("/test-cases/{test_case_id}/runs", response_model=list[schemas.TestRunOut])
def list_runs(test_case_id: int, db: Session = Depends(get_db)):
    return (
        db.query(models.TestRun)
        .filter(models.TestRun.test_case_id == test_case_id)
        .order_by(models.TestRun.id.desc())
        .all()
    )
