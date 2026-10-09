"""Shell out to the Node/Playwright project to execute a generated spec file."""

import json
import subprocess
from pathlib import Path

AUTOMATION_DIR = Path(__file__).resolve().parents[3] / "automation"
GENERATED_DIR = AUTOMATION_DIR / "tests" / "generated"


def write_spec(test_case_id: int, code: str) -> Path:
    GENERATED_DIR.mkdir(parents=True, exist_ok=True)
    spec_path = GENERATED_DIR / f"testcase_{test_case_id}.spec.ts"
    spec_path.write_text(code, encoding="utf-8")
    return spec_path


def run_spec(spec_path: Path, base_url: str) -> dict:
    """Run the given spec via `npx playwright test` and return the parsed JSON report."""
    env = {"PLAYWRIGHT_BASE_URL": base_url}
    result = subprocess.run(
        [
            "npx",
            "playwright",
            "test",
            spec_path.relative_to(AUTOMATION_DIR).as_posix(),
            "--reporter=json",
        ],
        cwd=str(AUTOMATION_DIR),
        capture_output=True,
        text=True,
        env={**_inherit_env(), **env},
    )
    stdout = result.stdout.strip()
    try:
        report = json.loads(stdout) if stdout else {}
    except json.JSONDecodeError:
        report = {"raw_stdout": stdout, "raw_stderr": result.stderr}
    report["_returncode"] = result.returncode
    if result.returncode != 0 and "raw_stderr" not in report:
        report["raw_stderr"] = result.stderr
    return report


def _inherit_env() -> dict:
    import os

    return dict(os.environ)
