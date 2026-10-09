"""Environment-based configuration, loaded from backend/.env."""

import os
import re

from dotenv import load_dotenv

load_dotenv()

BEDROCK_API_KEY = os.environ["BEDROCK_API_KEY"]
BEDROCK_MODEL_ID = os.environ["BEDROCK_MODEL_ID"]

_arn_region_match = re.match(r"arn:aws:bedrock:([a-z0-9-]+):", BEDROCK_MODEL_ID)
AWS_REGION = os.environ.get("AWS_REGION") or (
    _arn_region_match.group(1) if _arn_region_match else "us-east-1"
)

DOCUMENT_STORAGE_DIR = os.environ.get("DOCUMENT_STORAGE_DIR", "./document_storage")
