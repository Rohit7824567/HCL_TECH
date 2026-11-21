from pathlib import Path
import shutil
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_CELL_VERTICAL_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from pptx import Presentation
from pptx.util import Inches as PptInches, Pt as PptPt
from pptx.dml.color import RGBColor as PptColor
from pptx.enum.text import PP_ALIGN

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "frontend" / "public" / "documents"
OUT.mkdir(parents=True, exist_ok=True)
REPORT_SRC = ROOT / "docs" / "P050_Project_Understanding.docx"
REPORT_DST = OUT / "P050_Project_Understanding.docx"
if REPORT_SRC.exists():
    shutil.copy2(REPORT_SRC, REPORT_DST)

NAVY = "142844"
BLUE = "2E66A5"
TEAL = "14827F"
GOLD = "D6AD52"
PALE = "EEF3F8"
INK = "25364A"
MUTED = "66778B"

def shade(cell, fill):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:fill"), fill)
    tcPr.append(shd)

def set_cell_text(cell, text, bold=False, color=INK, size=9):
    cell.text = ""
    p = cell.paragraphs[0]
    p.paragraph_format.space_after = Pt(0)
    r = p.add_run(text)
    r.bold = bold
    r.font.name = "Aptos"
    r.font.size = Pt(size)
    r.font.color.rgb = RGBColor.from_string(color)
    cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER

def code_files():
    paths = [
        "backend/app/main.py", "backend/app/database/db.py", "backend/app/models/models.py",
        "backend/app/services/auth.py", "backend/app/services/ingest.py", "backend/app/analytics/service.py",
        "backend/alembic/env.py", "backend/alembic/versions/0001_initial_schema.py",
        "frontend/src/main.jsx", "frontend/src/App.jsx", "frontend/src/services/api.js",
        "frontend/src/components/AnalyticsShowcase.jsx", "frontend/src/styles.css",
        "streamlit_app/app.py", "backend/requirements.txt", "frontend/package.json"
    ]
    return [(p, (ROOT / p).read_text(encoding="utf-8", errors="replace")) for p in paths if (ROOT / p).is_file()]

doc = Document()
sec = doc.sections[0]
sec.top_margin = Inches(.62); sec.bottom_margin = Inches(.62)
sec.left_margin = Inches(.72); sec.right_margin = Inches(.72)
styles = doc.styles
styles["Normal"].font.name = "Aptos"; styles["Normal"].font.size = Pt(9.5); styles["Normal"].font.color.rgb = RGBColor.from_string(INK)
styles["Normal"].paragraph_format.space_after = Pt(5)
for name, size, color in [("Heading 1", 17, NAVY), ("Heading 2", 12.5, BLUE), ("Heading 3", 10.5, TEAL)]:
    s = styles[name]; s.font.name = "Aptos Display"; s.font.size = Pt(size); s.font.bold = True; s.font.color.rgb = RGBColor.from_string(color)

header = sec.header.paragraphs[0]
header.text = "P050  |  CUSTOMER PURCHASE BEHAVIOUR ANALYSIS"
header.style = styles["Caption"]
header.runs[0].font.color.rgb = RGBColor.from_string(MUTED)
header.runs[0].font.size = Pt(8)
footer = sec.footer.paragraphs[0]
footer.alignment = WD_ALIGN_PARAGRAPH.CENTER
footer.add_run("Rohit Kumar  •  MCA, 2nd Year  •  Source Code Documentation").font.size = Pt(8)

p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
p.paragraph_format.space_before = Pt(32)
r = p.add_run("ABES ENGINEERING COLLEGE")
r.bold = True; r.font.size = Pt(17); r.font.color.rgb = RGBColor.from_string(NAVY)
p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = p.add_run("DEPARTMENT OF COMPUTER APPLICATIONS  |  MCA")
r.bold = True; r.font.size = Pt(9); r.font.color.rgb = RGBColor.from_string(MUTED)
p = doc.add_paragraph(style="Title"); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
p.paragraph_format.space_before = Pt(22); p.paragraph_format.space_after = Pt(4)
r = p.add_run("Complete Source Code Documentation")
r.font.name = "Aptos Display"; r.font.size = Pt(26); r.font.bold = True; r.font.color.rgb = RGBColor.from_string(NAVY)
p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
r=p.add_run("Customer Purchase Behaviour Analysis")
r.font.size=Pt(15); r.font.bold=True; r.font.color.rgb=RGBColor.from_string(TEAL)
p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
r=p.add_run("PROJECT P050  •  DATA ANALYTICS")
r.bold=True; r.font.size=Pt(10); r.font.color.rgb=RGBColor.from_string(BLUE)

meta = [
    ("Project ID", "P050"), ("Student", "Rohit Kumar"), ("University number", "2500320140127"),
    ("Programme", "MCA, 2nd Year"), ("Mentor", "Mr. Chirag Jain"),
    ("Repository", "https://github.com/Rohit7824567/HCL_TECH"),
    ("Frontend", "JavaScript, React, Vite, Recharts, Tailwind CSS"),
    ("Backend and analytics", "Python, FastAPI, Pandas, NumPy, scikit-learn (dependency)"),
    ("Database and ORM", "SQLite locally; PostgreSQL supported; SQLAlchemy and Alembic"),
    ("Additional interface", "Streamlit with Plotly visualizations"),
]
t=doc.add_table(rows=0, cols=2); t.alignment=WD_TABLE_ALIGNMENT.CENTER; t.style="Table Grid"
for a,b in meta:
    cells=t.add_row().cells
    set_cell_text(cells[0],a,True,NAVY,9); shade(cells[0],PALE)
    set_cell_text(cells[1],b,False,INK,9)

doc.add_heading("Purpose and scope", level=1)
doc.add_paragraph("This manual documents the implementation of P050, a customer purchase analytics application. It explains the application layers, database model, data import and analytics flow, API routes, and the source files included in the code appendix. The code listings are taken from the project repository so the student and reviewer can trace the implementation directly.")
doc.add_heading("System overview", level=1)
doc.add_paragraph("The React dashboard sends authenticated requests to the FastAPI service. The API validates uploads, normalizes spreadsheet columns, stores customer, product, order and line-item records through SQLAlchemy, and computes dashboard measures from those records with Pandas. The Streamlit interface reuses the same backend models, import routine and analytics functions. SQLite is the local default; PostgreSQL can be selected through DATABASE_URL.")
tbl=doc.add_table(rows=1, cols=3); tbl.style="Table Grid"; tbl.alignment=WD_TABLE_ALIGNMENT.CENTER
for i,h in enumerate(["Layer","Main implementation","Responsibility"]):
    set_cell_text(tbl.rows[0].cells[i],h,True,"FFFFFF",9); shade(tbl.rows[0].cells[i],NAVY)
for row in [
    ("Web interface","React, Vite, Recharts","Authentication, navigation, upload UI, charts and analysis views"),
    ("API service","FastAPI, Pydantic","Authentication, protected analytics, imports, export and health check"),
    ("Analytics","Pandas and SQLAlchemy","Revenue summaries, product rankings, customer RFM segments and insights"),
    ("Persistence","SQLite / PostgreSQL","Relational storage for accounts, customers, products and orders"),
    ("Companion app","Streamlit, Plotly","Alternative dashboard using the same persisted data and analytics"),
]:
    cells=tbl.add_row().cells
    for i,val in enumerate(row): set_cell_text(cells[i],val,i==0,INK,8.5)

doc.add_heading("Processing workflow", level=1)
for s in [
    "A user registers or signs in. Passwords are hashed by the backend and the API returns a bearer token.",
    "The user uploads CSV or Excel data. The API checks file type and size, then reads the file into a Pandas DataFrame.",
    "The ingestion service maps common column aliases to the project schema, parses dates and numbers, removes invalid or duplicate rows, and inserts valid records transactionally.",
    "Dashboard and analysis requests query the persisted tables, calculate measures, and return JSON for the React charts and tables.",
    "A CSV export endpoint provides recorded transaction data. Import history tracks upload totals and accepted rows.",
]: doc.add_paragraph(s, style="List Number")

doc.add_heading("Data model", level=1)
for title, desc in [
    ("Customer", "Customer identifier, display name, optional contact and demographic attributes, and city."),
    ("Product", "Product identifier, name, category, unit price, and optional description."),
    ("Order", "Order identifier, customer relationship, date, total amount, payment method, and status."),
    ("OrderItem", "Product line within an order, including quantity, unit price, and subtotal."),
    ("DataImport and User", "Import audit counts and account credentials with a password hash."),
]:
    p=doc.add_paragraph(); p.paragraph_format.space_after=Pt(3)
    r=p.add_run(title+" — "); r.bold=True; r.font.color.rgb=RGBColor.from_string(BLUE); p.add_run(desc)

doc.add_heading("Analytics implemented", level=1)
for s in [
    "Business summary: total revenue, order count, unique customers, average order value, units, month-over-month growth and monthly revenue series.",
    "Product performance: revenue and units by product, and revenue contribution by category.",
    "Customer value: order recency, purchase frequency, monetary value, repeat purchase rate, average customer spend, and rule-based RFM segments.",
    "Business observations: revenue leader, retention opportunity, and latest-month revenue when source data is available.",
]: doc.add_paragraph(s, style="List Bullet")

doc.add_heading("API surface", level=1)
api_rows=[("POST","/api/auth/register","Create account and return token"),("POST","/api/auth/login","Verify credentials and return token"),("GET","/api/auth/me","Read current account"),("GET","/api/health","Check API and database"),("GET","/api/dashboard/summary","Dashboard measures"),("GET","/api/analytics/products","Product performance"),("GET","/api/analytics/customers","Customer RFM results"),("POST","/api/upload/csv or /api/upload/excel","Validate and import records"),("GET","/api/imports","Recent upload history"),("GET","/api/export/report","Download transaction CSV")]
t=doc.add_table(rows=1,cols=3);t.style="Table Grid"
for i,h in enumerate(["Method","Path","Purpose"]):set_cell_text(t.rows[0].cells[i],h,True,"FFFFFF",8.5);shade(t.rows[0].cells[i],NAVY)
for row in api_rows:
    cells=t.add_row().cells
    for i,val in enumerate(row):set_cell_text(cells[i],val,False,INK,8)

doc.add_heading("Run the project", level=1)
for cmd in ["Backend: python -m uvicorn app.main:app --reload --app-dir backend", "Frontend: cd frontend; npm run dev", "Open the Vite address printed in the terminal. The API defaults to port 8000; API documentation is at /docs."]:
    doc.add_paragraph(cmd, style="List Bullet")
doc.add_paragraph("Use the repository README for setup, environment variables and deployment notes. Protect AUTH_SECRET and DATABASE_URL, and configure CORS_ORIGINS for a deployed frontend. Imported data is shared across accounts in the current deployment; user-level row isolation is not implemented.")

doc.add_heading("Repository source inventory", level=1)
doc.add_paragraph("The appendix contains the current source text for the core backend, frontend, Streamlit application, migration and package manifests. The GitHub repository is the canonical location for the complete project and future revisions.")
for path, _ in code_files(): doc.add_paragraph(path, style="List Bullet")
doc.add_paragraph("GitHub repository: https://github.com/Rohit7824567/HCL_TECH")

for path, source in code_files():
    doc.add_page_break()
    doc.add_heading(path, level=1)
    p=doc.add_paragraph()
    p.paragraph_format.space_after=Pt(0)
    p.paragraph_format.line_spacing=1.0
    run=p.add_run(source.rstrip() or " ")
    run.font.name="Consolas"; run.font.size=Pt(6.7); run.font.color.rgb=RGBColor.from_string("24364B")
    run._element.rPr.rFonts.set(qn("w:eastAsia"),"Consolas")

docx_path = OUT / "P050_Complete_Source_Code_Documentation.docx"
doc.save(docx_path)

# Editable, downloadable slide presentation matching the project report.
prs=Presentation(); prs.slide_width=PptInches(13.333); prs.slide_height=PptInches(7.5)
def slide(title, kicker, lines, cover=False):
    s=prs.slides.add_slide(prs.slide_layouts[6])
    bg=s.background.fill; bg.solid(); bg.fore_color.rgb=PptColor.from_string(NAVY if cover else "F2F6FA")
    color=PptColor(255,255,255) if cover else PptColor.from_string(INK)
    k=s.shapes.add_textbox(PptInches(.7),PptInches(.55),PptInches(11.9),PptInches(.4)).text_frame
    k.text=kicker.upper(); k.paragraphs[0].font.size=PptPt(12); k.paragraphs[0].font.bold=True; k.paragraphs[0].font.color.rgb=PptColor.from_string(GOLD if cover else TEAL)
    tf=s.shapes.add_textbox(PptInches(.7),PptInches(1.3),PptInches(12),PptInches(1.25)).text_frame
    tf.text=title; tf.paragraphs[0].font.size=PptPt(32 if cover else 28); tf.paragraphs[0].font.bold=True; tf.paragraphs[0].font.color.rgb=color
    y=2.55 if cover else 2.3
    for line in lines:
        box=s.shapes.add_textbox(PptInches(.95),PptInches(y),PptInches(11.4),PptInches(.55)).text_frame
        box.text=line; box.paragraphs[0].font.size=PptPt(18); box.paragraphs[0].font.color.rgb=color; y+=.68
    foot=s.shapes.add_textbox(PptInches(.7),PptInches(7.05),PptInches(11.9),PptInches(.22)).text_frame
    foot.text="P050  •  ROHIT KUMAR  •  ABES ENGINEERING COLLEGE"; foot.paragraphs[0].font.size=PptPt(8); foot.paragraphs[0].font.color.rgb=PptColor.from_string("C7D2DF" if cover else MUTED)
    return s

slide("Customer Purchase Behaviour Analysis","Project P050 | Data Analytics",["Complete project presentation","Rohit Kumar  •  University No. 2500320140127","MCA, 2nd Year  •  Mentor: Mr. Chirag Jain","ABES Engineering College"],True)
slide("Project overview","01 | Context",["Analyze customer, product, order and revenue records in one workspace.","Goal: turn imported purchase data into understandable performance and customer insights.","Audience: business analysts and decision makers exploring transaction data."])
slide("Application architecture","02 | Implementation",["React and Vite dashboard communicates with a FastAPI JSON API.","Pandas analytics and SQLAlchemy persistence are shared with the Streamlit application.","SQLite supports local use; PostgreSQL is configurable for hosted environments."])
slide("Data import and quality","03 | Data workflow",["Accept CSV and Excel uploads with common column aliases.","Normalize dates and numeric values; reject invalid rows and duplicates.","Record import counts and store accepted customers, products, orders and line items."])
slide("Analytics","04 | Measures",["Revenue, orders, customers, average order value, units and monthly trend.","Product and category rankings, repeat purchase rate and average spend.","Rule-based RFM groups based on recency, frequency and monetary value."])
slide("Technology stack","05 | Product",["Programming: Python and JavaScript (React).","API and data: FastAPI, Pydantic, Pandas, SQLAlchemy, Alembic.","Visualization and storage: Recharts, Plotly, SQLite and PostgreSQL.","Tools: Vite, Streamlit and GitHub."])
slide("Limitations and next steps","06 | Review",["Current records are shared among accounts in one deployment.","RFM thresholds are explainable rules and should be calibrated to business context.","Potential extension: user-level data access, date filters and forecasting."])
slide("Project resources","07 | Submission",["Project report: downloadable from the project website footer.","Source documentation: core implementation listings are included in the manual.","GitHub: github.com/Rohit7824567/HCL_TECH","Prepared by Rohit Kumar  •  Mentor: Mr. Chirag Jain"])
pptx_path=OUT/"P050_Project_Presentation.pptx"
prs.save(pptx_path)
print(f"Created {docx_path} ({docx_path.stat().st_size} bytes)")
print(f"Created {pptx_path} ({pptx_path.stat().st_size} bytes)")
print(f"Copied report {REPORT_DST} ({REPORT_DST.stat().st_size if REPORT_DST.exists() else 0} bytes)")
