import pandas as pd
from datetime import date
from sqlalchemy.orm import Session
from app.models import Customer, Product, Order, OrderItem, DataImport

ALIASES={"customer_id":["customer_id","customerid","customer","client_id","clientid","member_id"],"customer_name":["customer_name","name","full_name"],"product_id":["product_id","productid","stock_code","stockcode","sku","item_id"],"product_name":["product_name","product","item","description","item_description"],"category":["category","product_category"],"order_id":["order_id","orderid","transaction_id","transactionid","invoice","invoice_no","invoiceno","receipt_id"],"order_date":["order_date","date","transaction_date","invoicedate","invoice_date","timestamp","purchase_date"],"quantity":["quantity","qty","units"],"unit_price":["unit_price","price","unitprice","selling_price"],"total_amount":["total_amount","amount","revenue","sales","line_total","subtotal"],"city":["city","town","country","region"],"payment_method":["payment_method","payment","tender"]}
def normalize(df):
    df=df.copy(); df.columns=[str(x).strip().lower().replace(" ","_") for x in df.columns]
    rename={}
    for target, aliases in ALIASES.items():
        for col in df.columns:
            if col in aliases: rename[col]=target; break
    return df.rename(columns=rename)

def ingest(db: Session, df: pd.DataFrame, filename: str):
    df=normalize(df)
    source_rows=len(df)
    if "order_id" not in df:
        df["order_id"]=[f"ROW-{i+1:08d}" for i in range(len(df))]
    required={"customer_id","product_id","order_date"}
    missing=sorted(required-set(df.columns))
    if missing: raise ValueError("Missing required columns: "+", ".join(missing))
    if "quantity" not in df: df["quantity"]=1
    if "unit_price" not in df:
        if "total_amount" in df:
            df["unit_price"]=pd.to_numeric(df.total_amount,errors="coerce") / pd.to_numeric(df.quantity,errors="coerce")
        else: raise ValueError("Include unit_price, price, or total_amount")
    df["quantity"]=pd.to_numeric(df.quantity,errors="coerce")
    df["unit_price"]=pd.to_numeric(df.unit_price,errors="coerce")
    df["order_date"]=pd.to_datetime(df.order_date,errors="coerce")
    df=df.dropna(subset=["customer_id","product_id","order_id","quantity","unit_price","order_date"])
    df=df[(df.quantity>0)&(df.unit_price>=0)].drop_duplicates()
    if df.empty: raise ValueError("No valid rows found after cleaning")
    order_totals=(df.assign(_line_total=df.quantity*df.unit_price).groupby("order_id")._line_total.sum().to_dict())
    existing_orders={x[0] for x in db.query(Order.order_id).filter(Order.order_id.in_(df.order_id.astype(str).unique())).all()}
    successful=0
    try:
        for _,r in df.iterrows():
            cid=str(r.customer_id); pid=str(r.product_id); oid=str(r.order_id)
            if oid in existing_orders:
                continue
            if not db.query(Customer).filter_by(customer_id=cid).first():
                db.add(Customer(customer_id=cid,customer_name=str(r.get("customer_name",cid)),city=str(r.get("city","Unknown"))))
            if not db.query(Product).filter_by(product_id=pid).first():
                db.add(Product(product_id=pid,product_name=str(r.get("product_name",pid)),category=str(r.get("category","Uncategorized")),unit_price=float(r.unit_price)))
            db.flush()
            order=db.query(Order).filter_by(order_id=oid).first()
            amount=float(order_totals[oid])
            if not order:
                order=Order(order_id=oid,customer_id=cid,order_date=r.order_date.date(),total_amount=amount,payment_method=str(r.get("payment_method","Unknown")),order_status="Completed")
                db.add(order); db.flush()
            itemid=f"{oid}:{pid}:{successful}"
            db.add(OrderItem(item_id=itemid,order_id=oid,product_id=pid,quantity=int(r.quantity),unit_price=float(r.unit_price),subtotal=float(r.quantity*r.unit_price)))
            successful+=1
        db.add(DataImport(file_name=filename,total_records=source_rows,successful_records=successful,failed_records=max(0,source_rows-successful),import_status="completed" if successful else "duplicate-only"))
        db.commit()
    except Exception:
        db.rollback(); raise
    return {"total_records":int(source_rows),"successful_records":successful,"failed_records":max(0,source_rows-successful)}
