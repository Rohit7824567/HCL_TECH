import os, sys
from pathlib import Path
import streamlit as st
import pandas as pd
import plotly.express as px

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT / "backend"))
from app.database.db import Base, engine, SessionLocal
from app.analytics.service import summary, product_analytics, customer_analytics, insights
from app.services.ingest import ingest
from app.models import Order

st.set_page_config(page_title="Northstar Intelligence",page_icon="N",layout="wide")
st.markdown("""
<style>
:root { color-scheme: light; }
.stApp, [data-testid="stAppViewContainer"] { background:#f0f4f9 !important; color:#24344a !important; }
[data-testid="stHeader"] { background:#ffffff !important; border-bottom:1px solid #e1e7ef; }
[data-testid="stMain"] .block-container { padding:1.2rem 2.3rem 2.5rem; max-width:1500px; }
[data-testid="stMain"] h1, [data-testid="stMain"] h2, [data-testid="stMain"] h3,
[data-testid="stMain"] [data-testid="stMarkdownContainer"] { color:#24344a !important; }
[data-testid="stMain"] p, [data-testid="stMain"] label, [data-testid="stMain"] [data-testid="stCaptionContainer"] { color:#687a90 !important; }
[data-testid="stSidebar"] { background:#302017 !important; border-right:1px solid #60442d; }
[data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2 { color:#e6c15c !important; }
[data-testid="stSidebar"] p, [data-testid="stSidebar"] label,
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"],
[data-testid="stSidebar"] [data-testid="stCaptionContainer"] { color:#fff4df !important; }
[data-testid="stSidebar"] [data-testid="stWidgetLabel"] { color:#e6c15c !important; }
[data-testid="stMetric"] { background:#ffffff; border:1px solid #e0e6ee; border-radius:10px; padding:15px 17px; box-shadow:0 2px 8px #203d5b08; }
[data-testid="stMetricLabel"] { color:#68778d !important; }
[data-testid="stMetricValue"] { color:#1e314a !important; }
[data-testid="stMetricDelta"] { font-size:12px; }
[data-testid="stAlert"] { border-radius:9px; }
[data-testid="stDataFrame"], [data-testid="stTable"] { border:1px solid #e0e6ee; border-radius:9px; overflow:hidden; }
[data-testid="stFileUploader"] section { background:#ffffff; border:1px dashed #a9bbcc; border-radius:10px; }
.northstar-topbar { display:flex; justify-content:space-between; align-items:center; padding:11px 16px; margin:0 0 24px; background:#ffffff; border:1px solid #e1e7ef; border-radius:10px; color:#687a90; font-size:13px; }
.northstar-topbar strong { color:#203149; font-weight:700; }
.northstar-status { color:#167f84; font-weight:700; }
.metric-card { background:#ffffff; border:1px solid #e0e6ee; border-radius:9px; padding:16px 18px; }
div.stButton > button[kind="primary"] { background:#167f84; border-color:#167f84; color:#ffffff; border-radius:7px; }
div.stButton > button[kind="primary"]:hover { background:#116c72; border-color:#116c72; }
</style>
""",unsafe_allow_html=True)
st.sidebar.title("Northstar")
st.sidebar.caption("CUSTOMER INTELLIGENCE")
page=st.sidebar.radio("Workspace",["Dashboard","Customer Analytics","Product Analytics","Sales Analytics","Data Management","Business Insights"])
st.sidebar.divider()
st.markdown('<div class="northstar-topbar"><span>Workspace <strong>/</strong> Northstar Intelligence</span><span class="northstar-status">●&nbsp; Customer analytics</span></div>',unsafe_allow_html=True)
st.sidebar.caption("Database connection")
try:
    Base.metadata.create_all(bind=engine)
    with engine.connect() as connection:
        connection.exec_driver_sql("SELECT 1")
    st.sidebar.success("Connected")
    st.sidebar.caption("To share records with the React dashboard, configure the same PostgreSQL DATABASE_URL in Streamlit Cloud Secrets. Otherwise, import the dataset here.")
except Exception as exc:
    st.sidebar.error("Database unavailable")
    st.error(f"The analytics app could not connect to its database. Configure DATABASE_URL or Streamlit secrets. Details: {exc}")
    st.stop()
db=SessionLocal()
try:
    s=summary(db); p=product_analytics(db); c=customer_analytics(db)
    if page=="Dashboard":
        st.caption("CUSTOMER PURCHASE ANALYSIS")
        st.title("Business overview")
        st.write("Live performance calculated from your database records.")
        a,b,d,e=st.columns(4)
        a.metric("Total revenue",f"${s['revenue']:,.2f}",f"{s['growth']}% latest-month change")
        b.metric("Orders",f"{s['orders']:,}")
        d.metric("Customers",f"{s['customers']:,}")
        e.metric("Average order value",f"${s['aov']:,.2f}")
        left,right=st.columns([1.4,1])
        with left:
            st.subheader("Monthly revenue")
            if s["monthly_revenue"]: st.plotly_chart(px.area(pd.DataFrame(s["monthly_revenue"]),x="month",y="total_amount",template="plotly_white",labels={"month":"Month","total_amount":"Revenue"}),use_container_width=True)
            else: st.info("Import transaction data to begin analyzing revenue.")
        with right:
            st.subheader("Revenue by category")
            if p["categories"]: st.plotly_chart(px.bar(pd.DataFrame(p["categories"]),x="revenue",y="category",orientation="h",template="plotly_white"),use_container_width=True)
            else: st.info("Category analytics appear after your first import.")
        st.subheader("Top products")
        if p["top_products"]: st.dataframe(pd.DataFrame(p["top_products"]),use_container_width=True,hide_index=True)
    elif page=="Customer Analytics":
        st.caption("CUSTOMER INTELLIGENCE");st.title("Customer analytics")
        a,b,d=st.columns(3);a.metric("Repeat purchase rate",f"{c['metrics']['repeat_rate']}%");b.metric("Average spend",f"${c['metrics']['avg_spend']:,.2f}");d.metric("Customers",len(c["rfm"]))
        if c["segments"]: st.plotly_chart(px.bar(pd.DataFrame(c["segments"]),x="segment",y="customers",color="segment",template="plotly_white"),use_container_width=True)
        if c["rfm"]: st.dataframe(pd.DataFrame(c["rfm"]),use_container_width=True,hide_index=True)
        else: st.info("RFM segments will be calculated after transaction data is imported.")
    elif page=="Product Analytics":
        st.caption("PRODUCT INTELLIGENCE");st.title("Product analytics")
        if p["top_products"]: st.plotly_chart(px.bar(pd.DataFrame(p["top_products"]),x="revenue",y="product_name",orientation="h",template="plotly_white"),use_container_width=True);st.dataframe(pd.DataFrame(p["top_products"]),use_container_width=True,hide_index=True)
        else: st.info("Import order line items to analyze products.")
    elif page=="Sales Analytics":
        st.caption("SALES PERFORMANCE");st.title("Sales analytics")
        if s["monthly_revenue"]: st.plotly_chart(px.line(pd.DataFrame(s["monthly_revenue"]),x="month",y="total_amount",markers=True,template="plotly_white"),use_container_width=True)
        else: st.info("Import transactions to see daily and monthly sales trends.")
        st.metric("Units sold",s["units"])
    elif page=="Data Management":
        st.caption("DATA OPERATIONS");st.title("Data management")
        st.write("Upload CSV or Excel data. Required columns: customer_id, product_id, order_id, order_date. Include quantity and unit_price (or amount).")
        file=st.file_uploader("Choose dataset",type=["csv","xlsx","xls"])
        if file and st.button("Validate and import",type="primary"):
            try:
                df=pd.read_csv(file) if file.name.lower().endswith(".csv") else pd.read_excel(file)
                st.write("Preview",df.head(8))
                outcome=ingest(db,df,file.name);st.success(f"Imported {outcome['successful_records']} valid rows.")
            except Exception as ex: st.error(str(ex))
        imports=pd.read_sql("SELECT file_name, upload_date, total_records, successful_records, import_status FROM data_imports ORDER BY upload_date DESC LIMIT 30",engine)
        st.subheader("Import history");st.dataframe(imports,use_container_width=True,hide_index=True)
        orders=pd.read_sql("SELECT order_id, customer_id, order_date, total_amount FROM orders ORDER BY order_date DESC",engine)
        st.download_button("Export transactions CSV",orders.to_csv(index=False),"transactions.csv","text/csv")
    else:
        st.caption("DECISION SUPPORT");st.title("Business insights")
        items=insights(db)
        if items:
            for item in items:
                with st.container(border=True): st.subheader(item["title"]);st.write(item["detail"])
        else: st.info("Insights appear once the database contains transaction records.")
        st.caption("Customer segments use order recency and frequency thresholds. Review thresholds against your business context.")
finally: db.close()
