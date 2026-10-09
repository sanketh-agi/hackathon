"""Generate a PowerPoint deck describing the AI Test Case Generator backend.

Run with the venv interpreter:
    ./.venv/Scripts/python build_presentation.py
Produces: AI_Test_Case_Generator.pptx
"""

from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE
from pptx.oxml.ns import qn

# ---------------------------------------------------------------- palette ----
INK = RGBColor(0x16, 0x18, 0x1D)        # near-black text
MUTED = RGBColor(0x6B, 0x72, 0x80)      # muted grey
PRIMARY = RGBColor(0x25, 0x63, 0xEB)    # blue
PRIMARY_DK = RGBColor(0x17, 0x3A, 0x8A) # deep blue
ACCENT = RGBColor(0x7C, 0x3A, 0xED)     # violet
SUCCESS = RGBColor(0x06, 0x76, 0x47)    # green
WARN = RGBColor(0xB4, 0x53, 0x09)       # amber
SURFACE = RGBColor(0xFF, 0xFF, 0xFF)    # white
CARD = RGBColor(0xF5, 0xF6, 0xF8)       # light grey card
CARD_BLUE = RGBColor(0xEA, 0xF2, 0xFE)  # faint blue card
BORDER = RGBColor(0xE3, 0xE6, 0xEA)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
DARK_BG = RGBColor(0x0F, 0x17, 0x2A)    # dark slide bg

EMU_W = Inches(13.333)
EMU_H = Inches(7.5)

prs = Presentation()
prs.slide_width = EMU_W
prs.slide_height = EMU_H
BLANK = prs.slide_layouts[6]


# ----------------------------------------------------------- helpers ---------
def slide():
    return prs.slides.add_slide(BLANK)


def _no_line(shape):
    shape.line.fill.background()


def rect(s, x, y, w, h, fill, line=None, line_w=0.75, shape=MSO_SHAPE.RECTANGLE,
         shadow=False):
    sp = s.shapes.add_shape(shape, x, y, w, h)
    sp.fill.solid()
    sp.fill.fore_color.rgb = fill
    if line is None:
        _no_line(sp)
    else:
        sp.line.color.rgb = line
        sp.line.width = Pt(line_w)
    sp.shadow.inherit = False
    if shadow:
        el = sp._element.spPr
        ef = el.makeelement(qn('a:effectLst'), {})
        sh = ef.makeelement(qn('a:outerShdw'),
                            {'blurRad': '90000', 'dist': '38100',
                             'dir': '5400000', 'rotWithShape': '0'})
        clr = sh.makeelement(qn('a:srgbClr'), {'val': '16181D'})
        alpha = clr.makeelement(qn('a:alpha'), {'val': '18000'})
        clr.append(alpha)
        sh.append(clr)
        ef.append(sh)
        el.append(ef)
    return sp


def text(s, x, y, w, h, runs, align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP,
         space_after=4, line_spacing=1.0, wrap=True):
    """runs: list of paragraphs; each paragraph is a list of (txt, size, color,
    bold, italic) run tuples."""
    tb = s.shapes.add_textbox(x, y, w, h)
    tf = tb.text_frame
    tf.word_wrap = wrap
    tf.vertical_anchor = anchor
    tf.margin_left = 0
    tf.margin_right = 0
    tf.margin_top = 0
    tf.margin_bottom = 0
    for i, para in enumerate(runs):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = align
        p.space_after = Pt(space_after)
        p.space_before = Pt(0)
        p.line_spacing = line_spacing
        for (txt, size, color, bold, *rest) in para:
            italic = rest[0] if rest else False
            r = p.add_run()
            r.text = txt
            r.font.size = Pt(size)
            r.font.color.rgb = color
            r.font.bold = bold
            r.font.italic = italic
            r.font.name = "Segoe UI"
    return tb


def R(txt, size, color=INK, bold=False, italic=False):
    return (txt, size, color, bold, italic)


def chip(s, x, y, label, fill, fg):
    w = Inches(0.28 + 0.092 * len(label))
    c = rect(s, x, y, w, Inches(0.33), fill, shape=MSO_SHAPE.ROUNDED_RECTANGLE)
    c.adjustments[0] = 0.5
    text(s, x, y, w, Inches(0.33), [[R(label, 11, fg, True)]],
         align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
    return w


def kicker(s, txt, x=Inches(0.7), y=Inches(0.55)):
    text(s, x, y, Inches(6), Inches(0.3), [[R(txt.upper(), 12, PRIMARY, True)]])


def title(s, txt, x=Inches(0.7), y=Inches(0.86), w=Inches(12), size=30):
    text(s, x, y, w, Inches(0.8), [[R(txt, size, INK, True)]])


def underline(s, x=Inches(0.72), y=Inches(1.5), w=Inches(0.9)):
    rect(s, x, y, w, Pt(4), PRIMARY, shape=MSO_SHAPE.ROUNDED_RECTANGLE)


def footer(s, n):
    text(s, Inches(0.7), Inches(7.08), Inches(8), Inches(0.3),
         [[R("AI Test Case Generator  ·  Automation Platform", 9, MUTED)]])
    text(s, Inches(11.6), Inches(7.08), Inches(1.1), Inches(0.3),
         [[R(f"{n:02d}", 9, MUTED, True)]], align=PP_ALIGN.RIGHT)


# ============================================================ SLIDE 1 — TITLE
s = slide()
rect(s, 0, 0, EMU_W, EMU_H, DARK_BG)
# decorative bands
rect(s, 0, 0, Inches(0.22), EMU_H, PRIMARY)
rect(s, Inches(0.22), 0, Inches(0.08), EMU_H, ACCENT)
# faint corner accent
rect(s, Inches(10.4), Inches(-1.2), Inches(4.5), Inches(4.5), PRIMARY_DK,
     shape=MSO_SHAPE.OVAL)
rect(s, Inches(11.6), Inches(4.6), Inches(3.6), Inches(3.6), RGBColor(0x1B, 0x2A, 0x4A),
     shape=MSO_SHAPE.OVAL)

text(s, Inches(0.9), Inches(1.7), Inches(9), Inches(0.4),
     [[R("HACKATHON  ·  QA AUTOMATION", 13, RGBColor(0x8F, 0xB4, 0xFF), True)]])
text(s, Inches(0.9), Inches(2.25), Inches(11.5), Inches(2),
     [[R("AI Test Case Generator", 50, WHITE, True)],
      [R("& Automation Platform", 50, RGBColor(0x9F, 0xC2, 0xFF), True)]],
     line_spacing=1.0)
text(s, Inches(0.92), Inches(4.5), Inches(10.5), Inches(1),
     [[R("From requirement workbooks to approved, traceable test cases — and "
         "runnable Playwright specs — powered by AWS Bedrock.", 16,
         RGBColor(0xC6, 0xCF, 0xDE))]], line_spacing=1.15)

for i, (lab) in enumerate(["FastAPI", "SQLite", "AWS Bedrock", "Playwright", "React"]):
    chip(s, Inches(0.92 + i * 1.55), Inches(5.75), lab,
         RGBColor(0x1B, 0x2A, 0x4A), RGBColor(0xBF, 0xD3, 0xFF))

text(s, Inches(0.9), Inches(6.75), Inches(11), Inches(0.4),
     [[R("Technical Overview  ·  Architecture  ·  Pipeline  ·  Roadmap", 12,
         RGBColor(0x7A, 0x89, 0xA6))]])


# ====================================================== SLIDE 2 — THE PROBLEM
s = slide()
rect(s, 0, 0, EMU_W, EMU_H, SURFACE)
kicker(s, "The Problem")
title(s, "Manual test authoring is slow, lossy, and hard to trace")
underline(s)

pains = [
    ("Hours per requirement", "QA engineers hand-write test cases from dense "
     "BRD/PRD and QBP workbooks — a repetitive, error-prone slog."),
    ("Traceability gaps", "When a requirement changes, nobody can quickly answer "
     "\"which test cases cover this rule?\" Coverage drifts silently."),
    ("Inconsistent quality", "Depth and phrasing vary by author; edge cases get "
     "missed and expected results are often vague."),
    ("Automation lag", "Turning an approved test case into a runnable Playwright "
     "spec is yet another manual, specialist step."),
]
x0, y0 = Inches(0.7), Inches(1.9)
cw, ch, gap = Inches(5.9), Inches(2.25), Inches(0.3)
for i, (h, body) in enumerate(pains):
    cx = x0 + (cw + gap) * (i % 2)
    cy = y0 + (ch + Inches(0.3)) * (i // 2)
    rect(s, cx, cy, cw, ch, CARD, line=BORDER, shape=MSO_SHAPE.ROUNDED_RECTANGLE,
         shadow=True)
    rect(s, cx, cy, Inches(0.12), ch, WARN, shape=MSO_SHAPE.ROUNDED_RECTANGLE)
    text(s, cx + Inches(0.4), cy + Inches(0.3), cw - Inches(0.7), Inches(0.5),
         [[R(h, 17, INK, True)]])
    text(s, cx + Inches(0.4), cy + Inches(0.9), cw - Inches(0.7), Inches(1.2),
         [[R(body, 13, MUTED)]], line_spacing=1.15)
footer(s, 2)


# ===================================================== SLIDE 3 — THE SOLUTION
s = slide()
rect(s, 0, 0, EMU_W, EMU_H, SURFACE)
kicker(s, "The Solution")
title(s, "One pipeline: workbook → rules → tests → scripts")
underline(s)

text(s, Inches(0.7), Inches(1.75), Inches(12), Inches(0.7),
     [[R("Upload a requirement/QBP Excel workbook. The platform extracts rules, "
         "an LLM drafts traceable test cases, a reviewer approves them, and "
         "approved cases become Playwright TypeScript specs — all in one place.",
         14, MUTED)]], line_spacing=1.2)

steps = [
    ("1", "Ingest", "Parse .xlsx; flatten sheets to text and auto-extract rule tables.", PRIMARY),
    ("2", "Generate", "Bedrock drafts customer-specific test cases per rule.", ACCENT),
    ("3", "Review", "Edit and approve drafts; every case traces to a requirement.", WARN),
    ("4", "Automate", "Convert approved cases into runnable Playwright specs.", SUCCESS),
]
x0 = Inches(0.7)
cw, ch = Inches(2.95), Inches(2.9)
gap = Inches(0.17)
y = Inches(2.75)
for i, (num, h, body, color) in enumerate(steps):
    cx = x0 + (cw + gap) * i
    rect(s, cx, y, cw, ch, SURFACE, line=BORDER, shape=MSO_SHAPE.ROUNDED_RECTANGLE,
         shadow=True)
    rect(s, cx, y, cw, Inches(0.14), color, shape=MSO_SHAPE.ROUNDED_RECTANGLE)
    circ = rect(s, cx + Inches(0.35), y + Inches(0.42), Inches(0.72), Inches(0.72),
                color, shape=MSO_SHAPE.OVAL)
    text(s, cx + Inches(0.35), y + Inches(0.42), Inches(0.72), Inches(0.72),
         [[R(num, 22, WHITE, True)]], align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
    text(s, cx + Inches(0.35), y + Inches(1.35), cw - Inches(0.7), Inches(0.5),
         [[R(h, 19, INK, True)]])
    text(s, cx + Inches(0.35), y + Inches(1.9), cw - Inches(0.6), Inches(0.9),
         [[R(body, 12.5, MUTED)]], line_spacing=1.12)
    if i < 3:
        text(s, cx + cw - Inches(0.02), y + Inches(1.25), Inches(0.25), Inches(0.4),
             [[R("→", 20, color, True)]], align=PP_ALIGN.CENTER)
footer(s, 3)


# ================================================= SLIDE 4 — TECH STACK
s = slide()
rect(s, 0, 0, EMU_W, EMU_H, SURFACE)
kicker(s, "Technology Stack")
title(s, "What the platform is built on")
underline(s)

groups = [
    ("Backend API", PRIMARY, [
        ("FastAPI 0.115", "Async Python web framework + Swagger UI"),
        ("Uvicorn", "ASGI server (run without --reload on Windows)"),
        ("Pydantic 2.10", "Request/response schemas & strict tool schemas"),
    ]),
    ("Data & Parsing", ACCENT, [
        ("SQLAlchemy 2.0", "ORM over the pipeline data model"),
        ("SQLite", "Single-file DB (automation.db), created at startup"),
        ("openpyxl", "Reads .xlsx sheets → text & rule tables"),
    ]),
    ("AI / LLM", SUCCESS, [
        ("AWS Bedrock", "Converse API, bearer-token auth via boto3"),
        ("Tool-forced output", "Model must call record_test_cases (strict JSON)"),
        ("boto3 ≥ 1.35", "bedrock-runtime client"),
    ]),
    ("Output & Frontend", WARN, [
        ("Playwright / TS", "Approved cases → .spec.ts automation"),
        ("React + Vite", "Reviewer UI at localhost:5173 (CORS allowed)"),
        ("Server-rendered HTML", "Traceability / audit report"),
    ]),
]
x0, y0 = Inches(0.7), Inches(1.85)
cw, ch, gx, gy = Inches(5.9), Inches(2.35), Inches(0.3), Inches(0.3)
for i, (gname, color, items) in enumerate(groups):
    cx = x0 + (cw + gx) * (i % 2)
    cy = y0 + (ch + gy) * (i // 2)
    rect(s, cx, cy, cw, ch, SURFACE, line=BORDER, shape=MSO_SHAPE.ROUNDED_RECTANGLE,
         shadow=True)
    rect(s, cx + Inches(0.3), cy + Inches(0.28), Inches(0.3), Inches(0.3), color,
         shape=MSO_SHAPE.OVAL)
    text(s, cx + Inches(0.75), cy + Inches(0.24), cw - Inches(1), Inches(0.4),
         [[R(gname, 16, INK, True)]])
    for j, (name, desc) in enumerate(items):
        iy = cy + Inches(0.85) + Inches(0.47) * j
        text(s, cx + Inches(0.35), iy, cw - Inches(0.7), Inches(0.45),
             [[R(f"{name}  ", 12.5, color, True), R(desc, 11.5, MUTED)]])
footer(s, 4)


# ================================================= SLIDE 5 — ARCHITECTURE
s = slide()
rect(s, 0, 0, EMU_W, EMU_H, SURFACE)
kicker(s, "System Architecture")
title(s, "Layered, synchronous request flow")
underline(s)

# layer bands
layers = [
    ("CLIENT", "React + Vite reviewer UI  ·  Swagger /docs  ·  curl", PRIMARY, CARD_BLUE),
    ("API  (FastAPI routers)",
     "customers · documents · rules · testcases · codegen · reports", PRIMARY_DK, CARD),
    ("SERVICES",
     "doc_parser  ·  extract_rules  ·  ai_client (Bedrock Converse)", ACCENT, CARD),
    ("PERSISTENCE  (SQLAlchemy ORM)",
     "Customer ─< Document ─< Rule ─< TestCase ─1 PlaywrightScript",
     SUCCESS, CARD),
]
x0 = Inches(0.9)
w = Inches(8.1)
y = Inches(1.95)
bh = Inches(1.08)
for i, (name, body, color, bg) in enumerate(layers):
    by = y + (bh + Inches(0.22)) * i
    rect(s, x0, by, w, bh, bg, line=BORDER, shape=MSO_SHAPE.ROUNDED_RECTANGLE,
         shadow=True)
    rect(s, x0, by, Inches(0.14), bh, color, shape=MSO_SHAPE.ROUNDED_RECTANGLE)
    text(s, x0 + Inches(0.4), by + Inches(0.16), w - Inches(0.7), Inches(0.4),
         [[R(name, 15, color, True)]])
    text(s, x0 + Inches(0.4), by + Inches(0.56), w - Inches(0.7), Inches(0.4),
         [[R(body, 12.5, INK)]])
    if i < len(layers) - 1:
        text(s, x0 + w / 2 - Inches(0.25), by + bh - Inches(0.03), Inches(0.5),
             Inches(0.3), [[R("↓", 16, MUTED, True)]], align=PP_ALIGN.CENTER)

# external side panel
px = Inches(9.4)
rect(s, px, y, Inches(3.1), Inches(2.38), DARK_BG,
     shape=MSO_SHAPE.ROUNDED_RECTANGLE, shadow=True)
text(s, px + Inches(0.3), y + Inches(0.24), Inches(2.6), Inches(0.4),
     [[R("EXTERNAL", 12, RGBColor(0x8F, 0xB4, 0xFF), True)]])
text(s, px + Inches(0.3), y + Inches(0.7), Inches(2.6), Inches(1.5),
     [[R("AWS Bedrock", 15, WHITE, True)],
      [R("Converse API", 12, RGBColor(0xC6, 0xCF, 0xDE))],
      [R("Inference-profile ARN", 11, RGBColor(0x8A, 0x97, 0xB2))],
      [R("Bearer-token auth", 11, RGBColor(0x8A, 0x97, 0xB2))]],
     line_spacing=1.1, space_after=3)

rect(s, px, y + Inches(2.7), Inches(3.1), Inches(2.15), CARD,
     line=BORDER, shape=MSO_SHAPE.ROUNDED_RECTANGLE, shadow=True)
text(s, px + Inches(0.3), y + Inches(2.92), Inches(2.6), Inches(0.4),
     [[R("KEY TRAITS", 12, ACCENT, True)]])
for j, t in enumerate(["Synchronous — no job queue",
                       "SQLite created at startup",
                       "No native doc blocks:", "  text-only to the model",
                       "CORS → localhost:5173"]):
    text(s, px + Inches(0.3), y + Inches(3.36) + Inches(0.3) * j, Inches(2.65),
         Inches(0.3), [[R("• " + t if not t.startswith("  ") else t, 10.5,
                          MUTED)]])
footer(s, 5)


# ================================================= SLIDE 6 — DATA MODEL
s = slide()
rect(s, 0, 0, EMU_W, EMU_H, SURFACE)
kicker(s, "Data Model")
title(s, "The schema encodes the pipeline")
underline(s)

entities = [
    ("Customer", PRIMARY, ["id, name", "created_at"]),
    ("Document", PRIMARY_DK, ["doc_type, filename", "extracted_text", "uploaded_at"]),
    ("Rule", ACCENT, ["sheet_name", "rule_name", "description, workflow"]),
    ("TestCase", WARN, ["title, steps_json", "expected_result", "priority, status",
                        "requirement_trace"]),
    ("PlaywrightScript", SUCCESS, ["code (.spec.ts)", "generated_at"]),
]
x0 = Inches(0.55)
cw = Inches(2.35)
ch = Inches(2.5)
gap = Inches(0.18)
y = Inches(2.3)
for i, (name, color, fields) in enumerate(entities):
    cx = x0 + (cw + gap) * i
    rect(s, cx, y, cw, ch, SURFACE, line=BORDER, shape=MSO_SHAPE.ROUNDED_RECTANGLE,
         shadow=True)
    rect(s, cx, y, cw, Inches(0.6), color, shape=MSO_SHAPE.ROUNDED_RECTANGLE)
    rect(s, cx, y + Inches(0.3), cw, Inches(0.3), color)  # square off bottom of header
    text(s, cx, y, cw, Inches(0.6), [[R(name, 14, WHITE, True)]],
         align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
    for j, f in enumerate(fields):
        text(s, cx + Inches(0.22), y + Inches(0.78) + Inches(0.37) * j,
             cw - Inches(0.4), Inches(0.35), [[R(f, 11, INK)]])
    if i < len(entities) - 1:
        text(s, cx + cw - Inches(0.03), y + Inches(0.95), Inches(0.25), Inches(0.4),
             [[R("─<", 15, MUTED, True)]], align=PP_ALIGN.CENTER)

text(s, Inches(0.55), Inches(5.1), Inches(12.2), Inches(0.5),
     [[R("One-to-many down the chain; TestCase → PlaywrightScript is one-to-one. ",
         13, MUTED),
       R("Deleting a Customer cascades to all documents, rules, test cases & scripts.",
         13, INK, True)]], line_spacing=1.2)

# notes row
notes = [
    ("Rule extraction", "Header row must contain Rule Name + Discreption (source "
     "spelling); aliases in COLUMN_ALIASES."),
    ("Draft → Approved", "Scripts can only be generated for status == approved."),
    ("No migrations", "Base.metadata.create_all at startup; change schema → delete DB."),
]
ny = Inches(5.75)
nw = Inches(3.95)
for i, (h, b) in enumerate(notes):
    nx = Inches(0.55) + (nw + Inches(0.17)) * i
    rect(s, nx, ny, nw, Inches(1.15), CARD, line=BORDER,
         shape=MSO_SHAPE.ROUNDED_RECTANGLE)
    text(s, nx + Inches(0.25), ny + Inches(0.14), nw - Inches(0.45), Inches(0.4),
         [[R(h, 12.5, PRIMARY, True)]])
    text(s, nx + Inches(0.25), ny + Inches(0.5), nw - Inches(0.45), Inches(0.6),
         [[R(b, 10.5, MUTED)]], line_spacing=1.08)
footer(s, 6)


# ================================================= SLIDE 7 — PIPELINE DETAIL
s = slide()
rect(s, 0, 0, EMU_W, EMU_H, SURFACE)
kicker(s, "End-to-End Flow")
title(s, "Six stages, each a router")
underline(s)

flow = [
    ("Upload", "POST /customers/{id}/documents", ".xlsx only → flatten sheets to "
     "text + persist one Rule per data row.", PRIMARY),
    ("List rules", "GET /rules", "Returns rules from the customer's most recently "
     "uploaded document.", PRIMARY_DK),
    ("Generate", "POST /test-cases/generate", "One rule at a time; Bedrock forced to "
     "call record_test_cases. Saved as draft.", ACCENT),
    ("Review", "PATCH + POST /approve", "Edit drafts, then approve. Approval stamps "
     "approved_at.", WARN),
    ("Generate script", "POST /generate-script", "Requires approved. Produces one "
     "plain-text .spec.ts (fences stripped).", SUCCESS),
    ("Report", "GET /report", "Server-rendered HTML traceability view + "
     "total/approved/draft counts.", RGBColor(0x0E, 0x7A, 0x8A)),
]
x0, y0 = Inches(0.7), Inches(1.95)
cw, ch = Inches(3.85), Inches(2.3)
gx, gy = Inches(0.22), Inches(0.28)
for i, (h, ep, body, color) in enumerate(flow):
    cx = x0 + (cw + gx) * (i % 3)
    cy = y0 + (ch + gy) * (i // 3)
    rect(s, cx, cy, cw, ch, SURFACE, line=BORDER, shape=MSO_SHAPE.ROUNDED_RECTANGLE,
         shadow=True)
    rect(s, cx, cy, Inches(0.12), ch, color, shape=MSO_SHAPE.ROUNDED_RECTANGLE)
    text(s, cx + Inches(0.35), cy + Inches(0.22), Inches(0.6), Inches(0.5),
         [[R(f"{i+1}", 22, color, True)]])
    text(s, cx + Inches(1.0), cy + Inches(0.27), cw - Inches(1.2), Inches(0.5),
         [[R(h, 17, INK, True)]])
    rect(s, cx + Inches(0.35), cy + Inches(0.9), cw - Inches(0.65), Inches(0.4),
         CARD_BLUE, shape=MSO_SHAPE.ROUNDED_RECTANGLE)
    text(s, cx + Inches(0.5), cy + Inches(0.9), cw - Inches(0.9), Inches(0.4),
         [[R(ep, 10.5, PRIMARY_DK, True)]], anchor=MSO_ANCHOR.MIDDLE)
    text(s, cx + Inches(0.35), cy + Inches(1.45), cw - Inches(0.65), Inches(0.8),
         [[R(body, 11.5, MUTED)]], line_spacing=1.12)
footer(s, 7)


# ================================================= SLIDE 8 — AI DESIGN
s = slide()
rect(s, 0, 0, EMU_W, EMU_H, SURFACE)
kicker(s, "AI Integration")
title(s, "Reliable, structured generation with Bedrock")
underline(s)

left = [
    ("Tool-forced JSON", "The model must call record_test_cases exactly once. Its "
     "input schema is the Pydantic GeneratedTestCaseList made strict — every object "
     "gets additionalProperties:false and all props required."),
    ("Traceability by design", "The system prompt (senior QA architect) requires each "
     "test case to cite a specific document/section in requirement_trace."),
    ("Text-only context", "The configured model rejects Converse document blocks, so "
     "workbooks are reduced to plain text at upload and sent as text blocks."),
]
ly = Inches(1.95)
for i, (h, b) in enumerate(left):
    cy = ly + Inches(1.55) * i
    rect(s, Inches(0.7), cy, Inches(6.7), Inches(1.4), CARD, line=BORDER,
         shape=MSO_SHAPE.ROUNDED_RECTANGLE, shadow=True)
    rect(s, Inches(0.7), cy, Inches(0.12), Inches(1.4), ACCENT,
         shape=MSO_SHAPE.ROUNDED_RECTANGLE)
    text(s, Inches(1.0), cy + Inches(0.18), Inches(6.2), Inches(0.4),
         [[R(h, 15, INK, True)]])
    text(s, Inches(1.0), cy + Inches(0.6), Inches(6.2), Inches(0.75),
         [[R(b, 11.5, MUTED)]], line_spacing=1.12)

# right code-ish panel
rx = Inches(7.7)
rect(s, rx, Inches(1.95), Inches(5.0), Inches(4.65), DARK_BG,
     shape=MSO_SHAPE.ROUNDED_RECTANGLE, shadow=True)
text(s, rx + Inches(0.35), Inches(2.2), Inches(4.4), Inches(0.4),
     [[R("record_test_cases  —  tool input", 12, RGBColor(0x8F, 0xB4, 0xFF), True)]])
code_lines = [
    ("{", RGBColor(0xC6, 0xCF, 0xDE)),
    ('  "test_cases": [{', RGBColor(0xC6, 0xCF, 0xDE)),
    ('     title            : str', RGBColor(0x9F, 0xC2, 0xFF)),
    ('     preconditions    : str', RGBColor(0x9F, 0xC2, 0xFF)),
    ('     steps[]          : str', RGBColor(0x9F, 0xC2, 0xFF)),
    ('     expected_result  : str', RGBColor(0x9F, 0xC2, 0xFF)),
    ('     priority         : enum', RGBColor(0x9F, 0xC2, 0xFF)),
    ('     requirement_trace: str', RGBColor(0x9F, 0xC2, 0xFF)),
    ('  }]', RGBColor(0xC6, 0xCF, 0xDE)),
    ("}", RGBColor(0xC6, 0xCF, 0xDE)),
    ("", INK),
    ("# strict: additionalProperties=false", RGBColor(0x6D, 0xD1, 0x9E)),
    ("# strict: all properties required", RGBColor(0x6D, 0xD1, 0x9E)),
]
for j, (ln, col) in enumerate(code_lines):
    text(s, rx + Inches(0.35), Inches(2.65) + Inches(0.29) * j, Inches(4.4),
         Inches(0.3), [[R(ln if ln else " ", 12, col, False)]])
# use monospace feel via name
footer(s, 8)


# ================================================= SLIDE 9 — HIGHLIGHTS / DESIGN
s = slide()
rect(s, 0, 0, EMU_W, EMU_H, SURFACE)
kicker(s, "Engineering Highlights")
title(s, "Deliberate design decisions")
underline(s)

cards = [
    ("Strict schema → no parsing", "Validation happens at the tool-call layer; "
     "the model retries on mismatch. No brittle text parsing.", PRIMARY),
    ("Single source of context", "ai_client builds an identical document-block set "
     "for both generation and codegen calls.", ACCENT),
    ("Resilient Playwright output", "Codegen prefers role/text/label selectors since "
     "the live DOM isn't inspected; markdown fences stripped.", SUCCESS),
    ("Graceful rule extraction", "Header aliasing + a 20-row scan; sheets missing "
     "required columns are skipped, failures logged not fatal.", WARN),
    ("Clear operational guardrails", "Run without --reload on Windows; delete the DB "
     "when the schema changes; DEBUG logs full prompts.", PRIMARY_DK),
    ("Audit & traceability", "Server-rendered report maps every test case back to its "
     "requirement with status + priority badges.", RGBColor(0x0E, 0x7A, 0x8A)),
]
x0, y0 = Inches(0.7), Inches(1.9)
cw, ch = Inches(3.85), Inches(2.3)
gx, gy = Inches(0.22), Inches(0.26)
for i, (h, b, color) in enumerate(cards):
    cx = x0 + (cw + gx) * (i % 3)
    cy = y0 + (ch + gy) * (i // 3)
    rect(s, cx, cy, cw, ch, SURFACE, line=BORDER, shape=MSO_SHAPE.ROUNDED_RECTANGLE,
         shadow=True)
    rect(s, cx + Inches(0.3), cy + Inches(0.3), Inches(0.5), Inches(0.5), color,
         shape=MSO_SHAPE.ROUNDED_RECTANGLE)
    text(s, cx + Inches(0.3), cy + Inches(0.3), Inches(0.5), Inches(0.5),
         [[R("✓", 18, WHITE, True)]], align=PP_ALIGN.CENTER,
         anchor=MSO_ANCHOR.MIDDLE)
    text(s, cx + Inches(0.3), cy + Inches(1.0), cw - Inches(0.6), Inches(0.5),
         [[R(h, 15, INK, True)]])
    text(s, cx + Inches(0.3), cy + Inches(1.5), cw - Inches(0.6), Inches(0.7),
         [[R(b, 11.5, MUTED)]], line_spacing=1.1)
footer(s, 9)


# ================================================= SLIDE 10 — ROADMAP + CLOSE
s = slide()
rect(s, 0, 0, EMU_W, EMU_H, DARK_BG)
rect(s, 0, 0, Inches(0.22), EMU_H, PRIMARY)
rect(s, Inches(0.22), 0, Inches(0.08), EMU_H, ACCENT)

text(s, Inches(0.9), Inches(0.7), Inches(6), Inches(0.4),
     [[R("ROADMAP & NEXT STEPS", 13, RGBColor(0x8F, 0xB4, 0xFF), True)]])
text(s, Inches(0.9), Inches(1.15), Inches(11), Inches(0.8),
     [[R("Where this goes next", 34, WHITE, True)]])

roadmap = [
    ("Async job queue", "Move multi-second Bedrock calls off the request thread."),
    ("Schema migrations", "Add Alembic so model changes don't require deleting the DB."),
    ("Batch generation", "Generate across many rules / documents in one pass."),
    ("Re-add spec execution", "Run generated Playwright specs and report results."),
    ("Auth & multi-tenant", "User accounts, roles, and per-tenant isolation."),
    ("Broader ingestion", "PDF/Word requirements once model/doc support allows."),
]
x0 = Inches(0.9)
cw, ch = Inches(5.7), Inches(1.15)
gx, gy = Inches(0.3), Inches(0.25)
y0 = Inches(2.2)
for i, (h, b) in enumerate(roadmap):
    cx = x0 + (cw + gx) * (i % 2)
    cy = y0 + (ch + gy) * (i // 2)
    rect(s, cx, cy, cw, ch, RGBColor(0x1B, 0x2A, 0x4A),
         shape=MSO_SHAPE.ROUNDED_RECTANGLE)
    rect(s, cx, cy, Inches(0.1), ch, ACCENT, shape=MSO_SHAPE.ROUNDED_RECTANGLE)
    text(s, cx + Inches(0.35), cy + Inches(0.16), cw - Inches(0.6), Inches(0.4),
         [[R(h, 15, WHITE, True)]])
    text(s, cx + Inches(0.35), cy + Inches(0.57), cw - Inches(0.6), Inches(0.5),
         [[R(b, 11.5, RGBColor(0xBF, 0xCB, 0xE2))]], line_spacing=1.05)

rect(s, Inches(0.9), Inches(6.5), Inches(11.5), Pt(2), RGBColor(0x2B, 0x3A, 0x5A))
text(s, Inches(0.9), Inches(6.65), Inches(9), Inches(0.5),
     [[R("Thank you  —  Questions?", 16, WHITE, True)]])
text(s, Inches(0.9), Inches(6.65), Inches(11.5), Inches(0.5),
     [[R("FastAPI · SQLite · AWS Bedrock · Playwright · React", 11,
         RGBColor(0x7A, 0x89, 0xA6))]], align=PP_ALIGN.RIGHT)


out = "AI_Test_Case_Generator.pptx"
prs.save(out)
print(f"Saved {out} with {len(prs.slides._sldIdLst)} slides")
