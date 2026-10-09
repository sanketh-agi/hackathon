import logging
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.db import Base, engine
from app.routers import codegen, customers, documents, reports, rules, testcases

logging.basicConfig(
    level=os.environ.get("LOG_LEVEL", "INFO"),
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)

Base.metadata.create_all(bind=engine)

app = FastAPI(title="AI Test Case Generator & Automation")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(customers.router)
app.include_router(documents.router)
app.include_router(rules.router)
app.include_router(testcases.router)
app.include_router(codegen.router)
app.include_router(reports.router)


@app.get("/health")
def health():
    return {"status": "ok"}
