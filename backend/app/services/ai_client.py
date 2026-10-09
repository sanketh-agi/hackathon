"""Central Amazon Bedrock integration (Converse API).

Keeps the document-context-building logic in one place so the generation
call and the codegen call build an identical set of document content
blocks for a given customer.
"""

import logging
import os
from typing import Any

import boto3
from botocore.exceptions import ClientError

from app import config
from app.models import Customer, Document, Rule, TestCase

logger = logging.getLogger(__name__)

os.environ.setdefault("AWS_BEARER_TOKEN_BEDROCK", config.BEDROCK_API_KEY)

MODEL_ID = config.BEDROCK_MODEL_ID

_client = None


def get_client():
    global _client
    if _client is None:
        _client = boto3.client("bedrock-runtime", region_name=config.AWS_REGION)
    return _client


SYSTEM_PROMPT = """You are a senior QA test architect. You write customer-specific, \
end-to-end and pointed test cases derived strictly from the requirement and reference \
documents provided (BRD/PRD, customer requirements, user stories, acceptance criteria, \
existing test cases, QBP documents).

Rules:
- Every test case must be traceable to a specific document and, where possible, a specific \
section or requirement within it. Record this in `requirement_trace`.
- Prefer precise, actionable steps a tester or automation script can execute without guessing.
- Cover both end-to-end flows and pointed/edge-case scenarios; avoid duplicating existing test \
cases found in the reference documents unless extending their coverage.
- Expected results must be objectively verifiable (specific text, state, or behavior), not vague.
"""


def _document_blocks(documents: list[Document]) -> list[dict[str, Any]]:
    """Build the ordered list of text content blocks for a Converse message.

    The configured model rejects Bedrock Converse `document` content blocks
    outright (`ValidationException: This model doesn't support documents`),
    so every document is reduced to plain text at upload time (see
    doc_parser.extract_text) and sent as a text block here.
    """
    blocks: list[dict[str, Any]] = []
    for doc in documents:
        header = f"{doc.doc_type}: {doc.filename}"
        if doc.extracted_text:
            blocks.append({"text": f"--- {header} ---\n{doc.extracted_text}"})
        else:
            blocks.append(
                {"text": f"--- {header} --- (no extractable text — likely a scanned/image-only file)"}
            )
    return blocks


def _customer_context_text(customer: Customer) -> str:
    return f"Customer: {customer.name}\n"


def _strict_schema(model_cls) -> dict[str, Any]:
    """Pydantic JSON schema, patched so every object requires all its properties."""
    schema = model_cls.model_json_schema()

    def patch(node: Any) -> None:
        if isinstance(node, dict):
            if node.get("type") == "object" or "properties" in node:
                node["additionalProperties"] = False
                if "properties" in node:
                    node["required"] = list(node["properties"].keys())
            for value in node.values():
                patch(value)
        elif isinstance(node, list):
            for item in node:
                patch(item)

    patch(schema)
    return schema


def _rule_block(rule: Rule) -> dict[str, Any]:
    return {
        "text": (
            f"--- Rule: {rule.rule_name} (sheet: {rule.sheet_name}) ---\n"
            f"Description: {rule.description}\n"
            f"Workflow: {rule.workflow}"
        )
    }


def generate_test_cases(
    customer: Customer,
    rule: Rule,
    instructions: str = "",
    count_hint: int | None = None,
) -> list[dict[str, Any]]:
    from app.schemas import GeneratedTestCaseList

    client = get_client()

    user_content: list[dict[str, Any]] = [_rule_block(rule)]
    request_text = _customer_context_text(customer)
    request_text += (
        "\nGenerate customer-specific, end-to-end and pointed test cases for the single rule above only."
    )
    if count_hint:
        request_text += f"\nAim for approximately {count_hint} test cases."
    if instructions:
        request_text += f"\nAdditional instructions: {instructions}"
    request_text += (
        "\n\nYou MUST respond by calling the `record_test_cases` tool exactly once with "
        "the full set of generated test cases. Do not respond with plain text."
    )
    user_content.append({"text": request_text})

    tool_schema = _strict_schema(GeneratedTestCaseList)
    tool_config = {
        "tools": [
            {
                "toolSpec": {
                    "name": "record_test_cases",
                    "description": "Record the generated test cases.",
                    "inputSchema": {"json": tool_schema},
                }
            }
        ],
    }

    logger.info(
        "generate_test_cases: customer_id=%s rule_id=%s instructions=%r count_hint=%s model=%s",
        customer.id, rule.id, instructions, count_hint, MODEL_ID,
    )
    logger.debug("generate_test_cases: request_text=%r", request_text)

    try:
        response = client.converse(
            modelId=MODEL_ID,
            system=[{"text": SYSTEM_PROMPT}],
            messages=[{"role": "user", "content": user_content}],
            toolConfig=tool_config,
            inferenceConfig={"maxTokens": 16000},
        )
    except ClientError as e:
        logger.error(
            "generate_test_cases: Converse call failed: %s",
            e.response.get("Error", {}),
            exc_info=True,
        )
        raise

    usage = response.get("usage", {})
    logger.info(
        "generate_test_cases: stopReason=%s usage=%s",
        response.get("stopReason"), usage,
    )

    content = response["output"]["message"]["content"]
    logger.debug("generate_test_cases: response content=%s", content)

    tool_use = next((block["toolUse"] for block in content if "toolUse" in block), None)
    if tool_use is None:
        text = next((block["text"] for block in content if "text" in block), "")
        logger.warning(
            "generate_test_cases: model did not call record_test_cases; full response=%s",
            content,
        )
        raise RuntimeError(
            f"Model did not call record_test_cases; it responded with text instead: {text[:500]}"
        )

    logger.debug("generate_test_cases: tool_use.input=%s", tool_use["input"])
    parsed = GeneratedTestCaseList.model_validate(tool_use["input"])
    logger.info("generate_test_cases: parsed %d test cases", len(parsed.test_cases))
    return [tc.model_dump() for tc in parsed.test_cases]


def generate_playwright_code(
    customer: Customer,
    documents: list[Document],
    test_case: TestCase,
) -> str:
    client = get_client()

    user_content: list[dict[str, Any]] = list(_document_blocks(documents))
    steps_text = "\n".join(f"- {step}" for step in test_case.steps_json)
    request_text = (
        f"{_customer_context_text(customer)}\n"
        "Convert the following APPROVED test case into a single, runnable Playwright "
        "TypeScript test file (using @playwright/test). Prefer resilient selectors "
        "(role/text/label-based) since the live DOM was not inspected. Output ONLY the "
        "TypeScript code, no prose, no markdown fences.\n\n"
        f"Test case: {test_case.title}\n"
        f"Preconditions: {test_case.preconditions}\n"
        f"Steps:\n{steps_text}\n"
        f"Expected result: {test_case.expected_result}\n"
    )
    user_content.append({"text": request_text})

    logger.info(
        "generate_playwright_code: test_case_id=%s customer_id=%s documents=%d model=%s",
        test_case.id, customer.id, len(documents), MODEL_ID,
    )

    try:
        response = client.converse(
            modelId=MODEL_ID,
            system=[{"text": SYSTEM_PROMPT}],
            messages=[{"role": "user", "content": user_content}],
            inferenceConfig={"maxTokens": 8000},
        )
    except ClientError as e:
        logger.error(
            "generate_playwright_code: Converse call failed: %s",
            e.response.get("Error", {}),
            exc_info=True,
        )
        raise

    logger.info(
        "generate_playwright_code: stopReason=%s usage=%s",
        response.get("stopReason"), response.get("usage", {}),
    )

    content = response["output"]["message"]["content"]
    logger.debug("generate_playwright_code: response content=%s", content)

    code = next((block["text"] for block in content if "text" in block), None)
    if code is None:
        logger.warning("generate_playwright_code: no text block in response; full content=%s", content)
        raise RuntimeError("Model response contained no text content block")

    return code.strip().removeprefix("```typescript").removeprefix("```ts").removesuffix("```").strip()
