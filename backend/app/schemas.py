from datetime import datetime

from pydantic import BaseModel, Field


# ---- Customer ----

class CustomerCreate(BaseModel):
    name: str
    app_url: str = ""
    config_json: dict = Field(default_factory=dict)


class CustomerOut(BaseModel):
    id: int
    name: str
    app_url: str
    config_json: dict
    created_at: datetime

    class Config:
        from_attributes = True


# ---- Document ----

class DocumentOut(BaseModel):
    id: int
    customer_id: int
    doc_type: str
    filename: str
    extracted_text_preview: str
    uploaded_at: datetime

    class Config:
        from_attributes = True


# ---- Rule ----

class RuleOut(BaseModel):
    id: int
    customer_id: int
    document_id: int
    sheet_name: str
    rule_name: str
    description: str
    workflow: str

    class Config:
        from_attributes = True


# ---- Test case structured-output schema (used with client.messages.parse) ----

class GeneratedTestCase(BaseModel):
    title: str = Field(description="Short, specific test case title")
    preconditions: str = Field(description="State required before executing the steps")
    steps: list[str] = Field(description="Ordered list of concrete, actionable steps")
    expected_result: str = Field(description="Observable, verifiable expected outcome")
    priority: str = Field(description="One of: critical, high, medium, low")
    requirement_trace: str = Field(
        description="Which rule this test case derives from, for audit traceability"
    )


class GeneratedTestCaseList(BaseModel):
    test_cases: list[GeneratedTestCase]


class TestCaseOut(BaseModel):
    id: int
    customer_id: int
    rule_id: int | None
    title: str
    preconditions: str
    steps_json: list
    expected_result: str
    priority: str
    requirement_trace: str
    status: str
    generated_at: datetime
    approved_at: datetime | None

    class Config:
        from_attributes = True


class TestCaseUpdate(BaseModel):
    title: str | None = None
    preconditions: str | None = None
    steps_json: list | None = None
    expected_result: str | None = None
    priority: str | None = None
    requirement_trace: str | None = None


class GenerateRequest(BaseModel):
    rule_id: int = Field(description="Which extracted rule to generate test cases for")
    instructions: str = Field(
        default="", description="Optional extra guidance for this generation pass, e.g. focus area"
    )
    count_hint: int | None = Field(default=None, description="Approximate number of test cases desired")


# ---- Playwright script / runs ----

class PlaywrightScriptOut(BaseModel):
    id: int
    test_case_id: int
    code: str
    generated_at: datetime

    class Config:
        from_attributes = True


class TestRunOut(BaseModel):
    id: int
    test_case_id: int
    status: str
    result_json: dict
    started_at: datetime
    finished_at: datetime | None

    class Config:
        from_attributes = True
