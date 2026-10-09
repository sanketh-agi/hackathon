# AI Test Case Generator & Playwright Automation

Generates customer-specific test cases from uploaded requirement/QBP documents using
Claude, lets you review/approve them, converts approved cases into Playwright tests,
and runs them on demand.

## Project layout

```
Automation/
├─ backend/          FastAPI + SQLite. Claude integration, document storage,
│                     test-case CRUD, Playwright codegen, run orchestration.
├─ automation/        Node + Playwright project. Backend writes generated
│                     .spec.ts files into automation/tests/generated/ and
│                     shells out to `npx playwright test` to run them.
├─ frontend/          React (Vite) UI.
├─ samples/           Dummy BRD/PRD/user-story/acceptance-criteria/existing
│                     test case/QBP .txt files for trying out the app.
└─ tools/
   ├─ node-v22.12.0-win-x64/   Portable Node.js (see "About the portable Node" below)
   └─ certs/zscaler-root-ca.pem  Corporate proxy root CA (see TLS note below)
```

## Which shell are you using?

Every command below is given for **both** Git Bash / WSL (`sh`) and **Windows
PowerShell**, since the syntax for setting environment variables and `PATH`
differs. Use whichever matches the terminal you actually have open — mixing them
(e.g. running `export ...` in PowerShell) will fail with
`The term 'export' is not recognized...`.

## Prerequisites

- **Python 3.10+** — used to create the backend virtual environment.
- **Node.js 18+** — used for the frontend and the Playwright automation project.
  This machine has **no system-wide Node.js install**, and the official MSI
  installer requires an interactive admin prompt that isn't available here, so a
  portable (no-admin) copy is checked into `tools/node-v22.12.0-win-x64/`. Every
  command below that uses `npm`/`npx`/`node` assumes you've either:
  - put that folder on your `PATH` for the session (command shown in each step), or
  - installed your own Node.js normally and use that instead (then skip the
    `export PATH=...` lines entirely).
- **An Anthropic API key** — required for the "Generate test cases" and "Generate
  Playwright script" actions. Everything else (creating customers, uploading
  documents, browsing, running already-generated tests) works without one.

### Corporate TLS-inspecting proxy (Zscaler) — read this if requests fail with SSL errors

This machine terminates outbound HTTPS through a corporate proxy (Zscaler) using its
own root CA. Windows itself trusts that CA (it's in the system certificate store), but
neither Node's bundled CA store nor Python's `anthropic` SDK (which bundles its own
CA list) trust it by default. Two consequences, both already worked around in this
repo:

1. **`npx playwright install`** needs Node to trust the proxy's cert when downloading
   browser binaries. Fixed by exporting the proxy's root CA once to
   `tools/certs/zscaler-root-ca.pem` and pointing `NODE_EXTRA_CA_CERTS` at it (already
   done for the current install — if you reinstall Playwright browsers on a machine
   with a similar corporate proxy, you may need to redo this: see "Re-exporting the
   corporate CA" below).
2. **The backend calling the real Anthropic API** needs the same trust. Fixed in code:
   set the environment variable `ANTHROPIC_TRUST_SYSTEM_CA=1` when running the
   backend, and `app/services/ai_client.py` will verify TLS against the OS
   certificate store instead of the SDK's bundled one. Harmless to set even if you're
   **not** behind a proxy like this — leave it unset in that case, or set it anyway,
   it just changes which trust store is consulted.

If you're running this on a different machine with no such proxy, you can ignore all
of this — plain `npm install`, `npx playwright install`, and an unset
`ANTHROPIC_TRUST_SYSTEM_CA` will work normally.

---

## One-time setup (do this once per machine)

### 1. Backend — create the virtual environment and install dependencies

**Git Bash:**
```sh
cd C:\Automation\backend
python -m venv .venv
./.venv/Scripts/pip install -r requirements.txt
```

**PowerShell:**
```powershell
cd C:\Automation\backend
python -m venv .venv
.\.venv\Scripts\pip.exe install -r requirements.txt
```

### 2. Automation (Playwright) — install Node deps and the Chromium browser

**Git Bash:**
```sh
cd C:\Automation\automation
export PATH="C:/Automation/tools/node-v22.12.0-win-x64:$PATH"   # skip if you have your own Node on PATH
npm install
export NODE_EXTRA_CA_CERTS="C:/Automation/tools/certs/zscaler-root-ca.pem"  # only on this/similar corporate networks
npx playwright install chromium
```

**PowerShell:**
```powershell
cd C:\Automation\automation
$env:PATH = "C:\Automation\tools\node-v22.12.0-win-x64;$env:PATH"   # skip if you have your own Node on PATH
npm install
$env:NODE_EXTRA_CA_CERTS = "C:\Automation\tools\certs\zscaler-root-ca.pem"  # only on this/similar corporate networks
npx playwright install chromium
```

### 3. Frontend — install Node deps

**Git Bash:**
```sh
cd C:\Automation\frontend
export PATH="C:/Automation/tools/node-v22.12.0-win-x64:$PATH"   # skip if you have your own Node on PATH
npm install
```

**PowerShell:**
```powershell
cd C:\Automation\frontend
$env:PATH = "C:\Automation\tools\node-v22.12.0-win-x64;$env:PATH"   # skip if you have your own Node on PATH
npm install
```

That's it for setup — `backend/.venv`, `automation/node_modules`, and
`frontend/node_modules` now exist and don't need to be recreated unless you delete them
or change dependencies.

---

## Running the service manually (every time)

You need **two long-running processes**: the backend API and the frontend dev server.
The Playwright automation project has nothing to start on its own — the backend shells
out to it (`npx playwright test`) each time you click "Run" in the UI.

### Terminal 1 — Backend

**Git Bash:**
```sh
cd C:\Automation\backend
export ANTHROPIC_API_KEY=sk-ant-...          # your real key — required for generation
export ANTHROPIC_TRUST_SYSTEM_CA=1            # only on this/similar corporate networks
./.venv/Scripts/python -m uvicorn app.main:app --port 8001
```

**PowerShell:**
```powershell
cd C:\Automation\backend
$env:ANTHROPIC_API_KEY = "sk-ant-..."         # your real key — required for generation
$env:ANTHROPIC_TRUST_SYSTEM_CA = "1"           # only on this/similar corporate networks
.\.venv\Scripts\python.exe -m uvicorn app.main:app --port 8000
```

Leave this running. Verify it's up (either shell):

```sh
curl http://localhost:8000/health
# {"status":"ok"}
```

API docs (Swagger UI): http://localhost:8000/docs

> **Note on `--reload`:** you can add `--reload` for auto-restart on code changes, but
> on this machine `uvicorn`'s reload watcher spawns a child worker process that can
> survive after you kill the parent (e.g. with Ctrl+C or `Stop-Process`), leaving a
> stale server still bound to port 8000 and silently serving old code. If a restart
> ever seems to have no effect, check what's actually listening on the port before
> assuming your code change is wrong:
> ```sh
> powershell.exe -NoProfile -Command "Get-NetTCPConnection -LocalPort 8000 | Select-Object OwningProcess"
> powershell.exe -NoProfile -Command "Stop-Process -Id <PID> -Force"
> ```
> Running without `--reload` and manually restarting when you change backend code
> avoids this entirely.

### Terminal 2 — Frontend

**Git Bash:**
```sh
cd C:\Automation\frontend
export PATH="C:/Automation/tools/node-v22.12.0-win-x64:$PATH"   # skip if you have your own Node on PATH
npm run dev
```

**PowerShell:**
```powershell
cd C:\Automation\frontend
$env:PATH = "C:\Automation\tools\node-v22.12.0-win-x64;$env:PATH"   # skip if you have your own Node on PATH
npm run dev
```

Verify it's up (either shell):

```sh
curl http://localhost:5173/
```

Open **http://localhost:5173** in your browser.

### Stopping everything

Ctrl+C in each terminal, or find and stop the listening processes:

```sh
powershell.exe -NoProfile -Command "Get-NetTCPConnection -LocalPort 8000,5173 | Select-Object LocalPort, OwningProcess"
powershell.exe -NoProfile -Command "Stop-Process -Id <PID> -Force"
```

---

## Using the app

1. **Customer** tab: create a customer with an application URL and optional JSON
   config, or select an existing one.
2. **Documents** tab: upload requirement/QBP artifacts. Sample dummy files for every
   document type are in `samples/` (`sample_brd.txt`, `sample_prd.txt`,
   `sample_user_story.txt`, `sample_acceptance_criteria.txt`,
   `sample_existing_test_case.txt`, `sample_qbp.txt`) — upload each with its matching
   type from the dropdown.
3. **Test Cases** tab: click **Generate test cases**. Claude reads all uploaded
   documents (via the Files API, with prompt caching reused across calls) and returns
   structured, traceable test cases. Edit inline if needed, then **Approve**.
4. Still on **Test Cases**: click **Generate Playwright script** on an approved case.
5. **Runs** tab: click **Run** to execute the generated Playwright spec against the
   customer's application URL and see pass/fail.
6. **Reports** tab: view the audit-ready traceability report (test case ↔ source
   document ↔ latest run result).

Steps 3 and 4 require a real `ANTHROPIC_API_KEY` on the backend (step 1 above);
everything else works without one.

---

## Re-exporting the corporate CA (if needed on a new machine)

If you set this up on another machine behind a similar TLS-inspecting proxy and
`npx playwright install` fails with `UNABLE_TO_GET_ISSUER_CERT_LOCALLY` /
`unable to get local issuer certificate`:

```powershell
$cert = Get-ChildItem -Path Cert:\LocalMachine\Root | Where-Object { $_.Subject -match 'Zscaler Root CA' } | Select-Object -First 1
[System.IO.File]::WriteAllText('C:\Automation\tools\certs\zscaler-root-ca.pem', "-----BEGIN CERTIFICATE-----`n" + [System.Convert]::ToBase64String($cert.RawData, [System.Base64FormattingOptions]::InsertLineBreaks) + "`n-----END CERTIFICATE-----")
```

Then re-run `npx playwright install chromium` with `NODE_EXTRA_CA_CERTS` pointed at
that file (as in setup step 2 above). Swap `'Zscaler Root CA'` for whatever your
proxy's root CA subject actually is if it's a different vendor.

## v1 scope notes

- Execution is manual-trigger only (no CI/webhook auto-run yet).
- Playwright codegen relies on the test case text + app URL, not a live DOM crawl, so
  selector accuracy may need a human pass for complex UIs.
- The audit report is a generic HTML traceability view, not a customer-specific QBP
  template.

See `C:\Users\00005628\.claude\plans\mellow-singing-chipmunk.md` for the full design
rationale (model choice, prompt caching strategy, data model).
