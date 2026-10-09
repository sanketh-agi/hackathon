import logging
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.db import Base, engine
from app.routers import codegen, customers, documents, reports, rules, runs, testcases

logging.basicConfig(
    level=os.environ.get("LOG_LEVEL", "INFO"),
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)

Base.metadata.create_all(bind=engine)

app = FastAPI(title="AI Test Case Generator & Automation")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(customers.router, prefix="/api")
app.include_router(documents.router, prefix="/api")
app.include_router(rules.router, prefix="/api")
app.include_router(testcases.router, prefix="/api")
app.include_router(codegen.router, prefix="/api")
app.include_router(runs.router, prefix="/api")
app.include_router(reports.router, prefix="/api")


@app.get("/health")
def health():
    return {"status": "ok"}
