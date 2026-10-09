import logging
import os

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app import config, models, schemas
from app.db import get_db
from app.services import doc_parser, extract_rules

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/customers/{customer_id}/documents", tags=["documents"])

VALID_DOC_TYPES = {"brd", "prd", "user_story", "acceptance_criteria", "existing_test_case", "qbp"}


@router.post("", response_model=schemas.DocumentOut)
async def upload_document(
    customer_id: int,
    doc_type: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    if doc_type not in VALID_DOC_TYPES:
        raise HTTPException(400, f"doc_type must be one of {sorted(VALID_DOC_TYPES)}")
    customer = db.get(models.Customer, customer_id)
    if not customer:
        raise HTTPException(404, "Customer not found")

    filename = file.filename or "document"
    if not doc_parser.is_supported(filename):
        raise HTTPException(400, "Only Excel files (.xlsx) are supported. Please upload an Excel workbook.")

    data = await file.read()
    text = doc_parser.extract_text(filename, data)
    print(f"text--<{text}")

    extracted_text = ""
    file_path = ""
    if text is not None:
        extracted_text = text
        preview = text[:500]
    else:
        customer_dir = os.path.join(config.DOCUMENT_STORAGE_DIR, str(customer_id))
        os.makedirs(customer_dir, exist_ok=True)
        file_path = os.path.join(customer_dir, filename)
        with open(file_path, "wb") as f:
            f.write(data)
        preview = "(workbook had no readable cell data — attached as-is)"

    document = models.Document(
        customer_id=customer_id,
        doc_type=doc_type,
        filename=filename,
        extracted_text=extracted_text,
        file_path=file_path,
        extracted_text_preview=preview,
    )
    db.add(document)
    db.commit()
    db.refresh(document)

    try:
        rules_by_sheet = extract_rules.extract_workbook_bytes(data)
    except Exception:
        logger.exception(
            "upload_document: rule extraction failed for customer_id=%s document_id=%s",
            customer_id, document.id,
        )
        rules_by_sheet = {}

    for sheet_name, rules in rules_by_sheet.items():
        for rule in rules:
            db.add(
                models.Rule(
                    customer_id=customer_id,
                    document_id=document.id,
                    sheet_name=sheet_name,
                    rule_name=rule.get("Rule Name", ""),
                    description=rule.get("Discreption", ""),
                    workflow=rule.get("Workflow", ""),
                )
            )
    db.commit()

    return document


@router.get("", response_model=list[schemas.DocumentOut])
def list_documents(customer_id: int, db: Session = Depends(get_db)):
    return (
        db.query(models.Document)
        .filter(models.Document.customer_id == customer_id)
        .order_by(models.Document.id.desc())
        .all()
    )
