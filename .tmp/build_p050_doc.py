from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_CELL_VERTICAL_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.enum.section import WD_SECTION
from pathlib import Path

out = Path(r'docs/P050_Project_Understanding.docx')
out.parent.mkdir(parents=True, exist_ok=True)
doc = Document()
sec = doc.sections[0]
sec.top_margin = Inches(0.68); sec.bottom_margin = Inches(0.65); sec.left_margin = Inches(0.78); sec.right_margin = Inches(0.78)
styles = doc.styles
styles['Normal'].font.name = 'Aptos'; styles['Normal'].font.size = Pt(10.2); styles['Normal'].font.color.rgb = RGBColor(40, 52, 66)
styles['Normal'].paragraph_format.space_after = Pt(5)
for name, size, color in [('Heading 1',16,'173A5E'),('Heading 2',12,'247E89')]:
    st=styles[name]; st.font.name='Aptos Display'; st.font.size=Pt(size); st.font.bold=True; st.font.color.rgb=RGBColor.from_string(color); st.paragraph_format.space_before=Pt(9); st.paragraph_format.space_after=Pt(4)
styles['Title'].font.name='Aptos Display'; styles['Title'].font.size=Pt(26); styles['Title'].font.bold=True; styles['Title'].font.color.rgb=RGBColor(18,48,75)

def shade(cell, fill):
    tcPr=cell._tc.get_or_add_tcPr(); shd=OxmlElement('w:shd'); shd.set(qn('w:fill'), fill); tcPr.append(shd)
def borders(table):
    tblPr=table._tbl.tblPr; b=OxmlElement('w:tblBorders')
    for edge in ('top','left','bottom','right','insideH','insideV'):
        el=OxmlElement('w:'+edge); el.set(qn('w:val'),'single'); el.set(qn('w:sz'),'5'); el.set(qn('w:color'),'D5DFE8'); b.append(el)
    tblPr.append(b)
def cell_margins(cell, top=100, start=120, bottom=100, end=120):
    tc=cell._tc; tcPr=tc.get_or_add_tcPr(); m=OxmlElement('w:tcMar')
    for key,val in [('top',top),('start',start),('bottom',bottom),('end',end)]:
        e=OxmlElement('w:'+key); e.set(qn('w:w'),str(val)); e.set(qn('w:type'),'dxa'); m.append(e)
    tcPr.append(m)
def add_hyperlink(paragraph, text, url):
    part=paragraph.part; rid=part.relate_to(url,'http://schemas.openxmlformats.org/officeDocument/2006/relationships/hyperlink',is_external=True)
    h=OxmlElement('w:hyperlink'); h.set(qn('r:id'),rid); r=OxmlElement('w:r'); pr=OxmlElement('w:rPr')
    c=OxmlElement('w:color'); c.set(qn('w:val'),'147A8A'); pr.append(c); u=OxmlElement('w:u'); u.set(qn('w:val'),'single'); pr.append(u); r.append(pr)
    t=OxmlElement('w:t'); t.text=text; r.append(t); h.append(r); paragraph._p.append(h)

p=doc.add_paragraph(style='Title'); p.alignment=WD_ALIGN_PARAGRAPH.CENTER; p.add_run('Customer Purchase Behaviour Analysis')
p=doc.add_paragraph(); p.alignment=WD_ALIGN_PARAGRAPH.CENTER
r=p.add_run('Project Understanding | Data Analytics'); r.bold=True; r.font.size=Pt(12); r.font.color.rgb=RGBColor(36,126,137)
p=doc.add_paragraph(); p.alignment=WD_ALIGN_PARAGRAPH.CENTER; p.paragraph_format.space_after=Pt(12)
p.add_run('Project ID P050').font.size=Pt(11)

rows=[('Project ID & Title','P050 - Customer Purchase Behaviour Analysis'),('Domain','Data Analytics'),('Student','Rohit Kumar'),('University Number','2500320140127'),('Programme','MCA, 2nd Year'),('Mentor','Mr. Chirag Jain'),('Product','Full-stack customer purchase analytics platform'),('Repository','https://github.com/Rohit7824567/HCL_TECH')]
t=doc.add_table(rows=0, cols=2); t.alignment=WD_TABLE_ALIGNMENT.CENTER; t.autofit=False; t.columns[0].width=Inches(1.8); t.columns[1].width=Inches(5.55)
for i,(k,v) in enumerate(rows):
    cells=t.add_row().cells; cells[0].width=Inches(1.8); cells[1].width=Inches(5.55)
    cells[0].text=k; cells[1].text=''
    if k=='Repository': add_hyperlink(cells[1].paragraphs[0],v,v)
    else: cells[1].paragraphs[0].add_run(v)
    for j,c in enumerate(cells):
        c.vertical_alignment=WD_CELL_VERTICAL_ALIGNMENT.CENTER; cell_margins(c)
        if j==0:
            shade(c,'DCE9F1')
            for run in c.paragraphs[0].runs: run.bold=True; run.font.color.rgb=RGBColor(23,58,94)
        elif i%2==1: shade(c,'F7FAFC')
borders(t)

def heading(txt, level=1): doc.add_heading(txt, level=level)
def para(txt): doc.add_paragraph(txt)
def bullets(items):
    for x in items: doc.add_paragraph(x, style='List Bullet')

heading('1. Introduction and Purpose')
para('This project builds a customer purchase analysis and business intelligence platform for turning transaction records into clear, usable summaries. Users can import a CSV or Excel workbook, review sales and customer metrics, and explore product performance and customer segments through a web dashboard. The work demonstrates an end-to-end data analytics workflow, from data validation and storage through analysis and visual reporting.')
heading('2. Problem Statement and Objectives')
para('Purchase data often sits in spreadsheets that make it difficult to compare revenue over time, understand product demand, or identify repeat and at-risk customers. The platform provides a consistent import path and a shared view of these measures so a student analyst or small business user can explore the available records.')
bullets(['Accept transaction data from CSV and Excel files and validate expected fields.','Summarize revenue, orders, customer counts, average order value, and units sold.','Analyze monthly sales, product/category performance, repeat purchasing, and RFM customer groups.','Present results through an interactive dashboard and downloadable report.'])
heading('3. Project Scope and Workflow')
para('A user signs in, uploads a transaction file, and receives an import result. The backend reads the file, checks and normalizes rows, then stores accepted customers, products, orders, and order items. Analytics queries aggregate the stored records, and the React dashboard displays the results through charts, tables, and a rotatable 3D RFM customer map.')

heading('4. Technology Stack')
t2=doc.add_table(rows=1, cols=3); t2.alignment=WD_TABLE_ALIGNMENT.CENTER; t2.autofit=False
widths=[1.55,2.15,3.65]
for i,h in enumerate(['Layer','Languages / tools','Purpose']):
    c=t2.rows[0].cells[i]; c.text=h; c.width=Inches(widths[i]); shade(c,'173A5E');
    for run in c.paragraphs[0].runs: run.bold=True; run.font.color.rgb=RGBColor(255,255,255)
stack=[('Frontend','JavaScript, React, Vite','Browser interface, navigation, dashboard and upload experience.'),('Backend API','Python, FastAPI, Pydantic','Authentication, API endpoints, file validation and report export.'),('Analytics','Python, Pandas, NumPy, scikit-learn','Data cleanup and aggregation; scikit-learn is included for analytical extensions.'),('Charts','Recharts, Plotly','Dashboard charts and interactive visual analysis in the Streamlit app.'),('Database access','SQLAlchemy, Alembic','ORM models, database sessions and schema migration support.'),('Data storage','SQLite locally; PostgreSQL for deployment','Persists customer, product, order, item, user and import-history records.'),('Additional formats','CSV, XLSX via openpyxl','Data import and spreadsheet interchange.')]
for ri,row in enumerate(stack):
    cells=t2.add_row().cells
    for i,val in enumerate(row):
        cells[i].text=val; cells[i].width=Inches(widths[i]); cells[i].vertical_alignment=WD_CELL_VERTICAL_ALIGNMENT.CENTER; cell_margins(cells[i],80,100,80,100)
        if ri%2==0: shade(cells[i],'F4F8FB')
borders(t2)

heading('5. Data and Storage Design')
para('The primary data unit is a transaction line: one row for each product included in an order. Required import fields include customer_id, product_id, order_id, order_date, quantity, and unit_price. Descriptive fields such as customer_name, city, product_name, category, and payment_method can supplement the required fields. The database stores customers and products separately from orders and their order items, which avoids repeating the same customer and order details for every product line.')
para('SQLite is the zero-configuration local database. The same SQLAlchemy models support PostgreSQL when the DATABASE_URL setting points to a hosted database. The project also includes Alembic migration scaffolding. Account authentication protects API actions; imported workspace records are shared across accounts in the current implementation.')

heading('6. Analytics and Visual Outputs')
bullets(['Revenue and average order value from stored order totals.','Monthly revenue trends and product/category revenue and units sold.','Customer recency, frequency, and monetary value (RFM), with rule-based customer groups.','Repeat purchase rate and summary insights derived from imported records.','Interactive charts, customer value mapping, transaction tables, and report export.'])
para('RFM recency measures days since a customer’s latest order, frequency counts distinct orders, and monetary value sums order value. The current project uses transparent rule thresholds for labels such as Champions, Loyal, Potential Loyalists, New, At Risk, and Lost. These labels describe the stored data and do not predict future behavior.')

heading('7. Quality, Security, and Limitations')
para('The upload service accepts CSV and Excel formats, applies file-size and type checks, and validates rows before persistence. Passwords are hashed and the API uses bearer tokens. Deployment requires environment-specific settings such as DATABASE_URL, AUTH_SECRET, and CORS_ORIGINS. Credentials must remain in server-side environment settings rather than the browser bundle.')
para('Current limitations include shared imported records across accounts, rule-based rather than predictive customer segments, and no calibrated customer lifetime value or clustering model. Dashboard findings depend on the completeness and correctness of the uploaded data. Sample data should be identified as sample data and should not be reported as real business performance.')

heading('8. Expected Deliverables and Success Criteria')
bullets(['Working React dashboard and FastAPI service, with the companion Streamlit analytics app.','CSV/XLSX upload, validation, database persistence, analytics views, and CSV report export.','Project report and presentation describing purpose, workflow, technology, data design, and limitations.','Successful operation when a valid account can authenticate, a correctly structured file imports, and dashboard metrics reflect the persisted records.'])
heading('9. Repository')
p=doc.add_paragraph(); p.add_run('Source code: '); add_hyperlink(p,'github.com/Rohit7824567/HCL_TECH','https://github.com/Rohit7824567/HCL_TECH')

footer=sec.footer.paragraphs[0]; footer.alignment=WD_ALIGN_PARAGRAPH.CENTER
run=footer.add_run('P050  |  Customer Purchase Behaviour Analysis  |  Rohit Kumar'); run.font.size=Pt(8); run.font.color.rgb=RGBColor(110,126,142)
doc.core_properties.title='P050 Customer Purchase Behaviour Analysis - Project Understanding'
doc.core_properties.author='Rohit Kumar'
doc.core_properties.subject='MCA 2nd Year Data Analytics project'
doc.save(out)
print(out.resolve())
