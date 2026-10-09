from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import models, schemas
from app.db import get_db

router = APIRouter(prefix="/customers/{customer_id}/rules", tags=["rules"])


@router.get("", response_model=list[schemas.RuleOut])
def list_rules(customer_id: int, db: Session = Depends(get_db)):
    """Rules extracted from the most recently uploaded document for this customer."""
    customer = db.get(models.Customer, customer_id)
    if not customer:
        raise HTTPException(404, "Customer not found")

    latest_document = (
        db.query(models.Document)
        .filter(models.Document.customer_id == customer_id)
        .order_by(models.Document.id.desc())
        .first()
    )
    if not latest_document:
        return []

    return (
        db.query(models.Rule)
        .filter(models.Rule.document_id == latest_document.id)
        .order_by(models.Rule.id.asc())
        .all()
    )
