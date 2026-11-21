import io, logging
import pandas as pd
from fastapi import FastAPI, Depends, UploadFile, File, HTTPException, Query, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from app.database.db import Base, engine, get_db
from app.models import Order, DataImport, User
from app.analytics.service import summary, product_analytics, customer_analytics, insights
from app.services.ingest import ingest
from app.services.auth import hash_password, verify_password, create_token, read_token
from pydantic import BaseModel, EmailStr, Field

logging.basicConfig(level=logging.INFO)
Base.metadata.create_all(bind=engine)
app=FastAPI(title="Customer Purchase Intelligence API",version="1.0.0")
import os
cors_origins=os.getenv("CORS_ORIGINS")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[x.strip() for x in cors_origins.split(",")] if cors_origins else ["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_origin_regex=None if cors_origins else r"^https?://(?:localhost|127\.0\.0\.1|10(?:\.\d{1,3}){3}|192\.168(?:\.\d{1,3}){2}|172\.(?:1[6-9]|2\d|3[01])(?:\.\d{1,3}){2}|169\.254(?:\.\d{1,3}){2}):5173$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class RegisterRequest(BaseModel):
    full_name: str = Field(min_length=2, max_length=200)
    email: EmailStr
    password: str = Field(min_length=10, max_length=128)

class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=128)

def public_user(user): return {"id": user.id, "email": user.email, "full_name": user.full_name}

def require_user(authorization: str | None = Header(default=None), db: Session = Depends(get_db)):
    token = authorization.removeprefix("Bearer ") if authorization and authorization.startswith("Bearer ") else ""
    claims = read_token(token)
    if not claims: raise HTTPException(401, "Please sign in to access this data")
    user = db.get(User, int(claims["sub"]))
    if not user: raise HTTPException(401, "Account no longer exists")
    return user

@app.post("/api/auth/register")
def register(body: RegisterRequest, db: Session = Depends(get_db)):
    email = body.email.lower()
    if db.query(User).filter_by(email=email).first(): raise HTTPException(409, "An account with this email already exists")
    user = User(email=email, full_name=body.full_name.strip(), password_hash=hash_password(body.password))
    db.add(user); db.commit(); db.refresh(user)
    return {"access_token": create_token(user.id, user.email), "token_type":"bearer", "user":public_user(user)}

@app.post("/api/auth/login")
def login(body: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter_by(email=body.email.lower()).first()
    if not user or not verify_password(body.password, user.password_hash): raise HTTPException(401, "Email or password is incorrect")
    return {"access_token": create_token(user.id, user.email), "token_type":"bearer", "user":public_user(user)}

@app.get("/api/auth/me")
def current_user(authorization: str | None = Header(default=None), db: Session = Depends(get_db)):
    token = authorization.removeprefix("Bearer ") if authorization and authorization.startswith("Bearer ") else ""
    claims = read_token(token)
    if not claims: raise HTTPException(401, "Your session has expired. Please sign in again.")
    user = db.get(User, int(claims["sub"]))
    if not user: raise HTTPException(401, "Account no longer exists")
    return public_user(user)

@app.get("/api/health")
def health(db:Session=Depends(get_db)):
    try: db.execute(__import__("sqlalchemy").text("SELECT 1")); return {"status":"ok","database":"connected"}
    except Exception as e: raise HTTPException(503,"Database unavailable") from e
@app.get("/api/dashboard/summary", dependencies=[Depends(require_user)])
def dashboard(db:Session=Depends(get_db)): return summary(db)
@app.get("/api/analytics/revenue", dependencies=[Depends(require_user)])
def revenue(db:Session=Depends(get_db)): return {"monthly":summary(db)["monthly_revenue"]}
@app.get("/api/analytics/sales-trends", dependencies=[Depends(require_user)])
def sales(db:Session=Depends(get_db)): return {"monthly":summary(db)["monthly_revenue"]}
@app.get("/api/analytics/products", dependencies=[Depends(require_user)])
def products(db:Session=Depends(get_db)): return product_analytics(db)
@app.get("/api/analytics/customers", dependencies=[Depends(require_user)])
def customers(db:Session=Depends(get_db)): return customer_analytics(db)
@app.get("/api/analytics/customer-segments", dependencies=[Depends(require_user)])
def segments(db:Session=Depends(get_db)): return {"segments":customer_analytics(db)["segments"]}
@app.get("/api/insights", dependencies=[Depends(require_user)])
def get_insights(db:Session=Depends(get_db)): return {"insights":insights(db)}
@app.get("/api/transactions", dependencies=[Depends(require_user)])
def transactions(page:int=Query(1,ge=1),limit:int=Query(20,ge=1,le=200),db:Session=Depends(get_db)):
    q=db.query(Order).order_by(Order.order_date.desc()); total=q.count(); rows=q.offset((page-1)*limit).limit(limit).all()
    return {"total":total,"page":page,"items":[{"order_id":x.order_id,"customer_id":x.customer_id,"order_date":x.order_date.isoformat(),"total_amount":x.total_amount,"payment_method":x.payment_method} for x in rows]}
@app.get("/api/transactions/{order_id}", dependencies=[Depends(require_user)])
def transaction(order_id:str,db:Session=Depends(get_db)):
    x=db.query(Order).filter_by(order_id=order_id).first()
    if not x: raise HTTPException(404,"Transaction not found")
    return {"order_id":x.order_id,"customer_id":x.customer_id,"order_date":x.order_date.isoformat(),"total_amount":x.total_amount,"payment_method":x.payment_method,"items":[{"product_id":i.product_id,"quantity":i.quantity,"subtotal":i.subtotal} for i in x.items]}
async def upload(file:UploadFile,db:Session):
    name=file.filename or "upload.csv"
    if not name.lower().endswith((".csv",".xlsx",".xls")): raise HTTPException(400,"Upload a CSV or Excel file")
    data=await file.read()
    if len(data)>20*1024*1024: raise HTTPException(413,"File exceeds 20 MB limit")
    try:
        df=pd.read_csv(io.BytesIO(data)) if name.lower().endswith(".csv") else pd.read_excel(io.BytesIO(data))
        return ingest(db,df,name)
    except ValueError as e: raise HTTPException(422,str(e))
    except Exception as e: logging.exception("Import failed"); raise HTTPException(400,"Unable to process file") from e
@app.post("/api/upload/csv", dependencies=[Depends(require_user)])
async def upload_csv(file:UploadFile=File(...),db:Session=Depends(get_db)): return await upload(file,db)
@app.post("/api/upload/excel", dependencies=[Depends(require_user)])
async def upload_excel(file:UploadFile=File(...),db:Session=Depends(get_db)): return await upload(file,db)
@app.get("/api/imports", dependencies=[Depends(require_user)])
def imports(db:Session=Depends(get_db)):
    return [{"file_name":x.file_name,"upload_date":x.upload_date.isoformat(),"total_records":x.total_records,"successful_records":x.successful_records,"failed_records":x.failed_records,"status":x.import_status} for x in db.query(DataImport).order_by(DataImport.upload_date.desc()).limit(50)]
@app.get("/api/export/report", dependencies=[Depends(require_user)])
def export(db:Session=Depends(get_db)):
    rows=[{"order_id":o.order_id,"customer_id":o.customer_id,"order_date":o.order_date,"total_amount":o.total_amount} for o in db.query(Order).all()]
    buf=io.StringIO(); pd.DataFrame(rows).to_csv(buf,index=False)
    return StreamingResponse(iter([buf.getvalue()]),media_type="text/csv",headers={"Content-Disposition":"attachment; filename=transactions.csv"})
