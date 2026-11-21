import pandas as pd
from sqlalchemy.orm import Session
from app.models import Customer, Product, Order, OrderItem

def frames(db: Session):
    orders = pd.DataFrame([{"order_id":o.order_id,"customer_id":o.customer_id,"order_date":o.order_date,"total_amount":o.total_amount} for o in db.query(Order).all()])
    customers = pd.DataFrame([{"customer_id":c.customer_id,"customer_name":c.customer_name,"city":c.city} for c in db.query(Customer).all()])
    products = pd.DataFrame([{"product_id":p.product_id,"product_name":p.product_name,"category":p.category} for p in db.query(Product).all()])
    items = pd.DataFrame([{"order_id":i.order_id,"product_id":i.product_id,"quantity":i.quantity,"subtotal":i.subtotal} for i in db.query(OrderItem).all()])
    if not orders.empty: orders["order_date"] = pd.to_datetime(orders.order_date)
    return orders, customers, products, items

def summary(db: Session):
    o,c,p,i=frames(db)
    revenue=float(o.total_amount.sum()) if not o.empty else 0
    monthly=o.assign(month=o.order_date.dt.to_period("M").astype(str)).groupby("month").total_amount.sum().reset_index().to_dict("records") if not o.empty else []
    growth=None
    if len(monthly)>1 and monthly[-2]["total_amount"]: growth=round((monthly[-1]["total_amount"]-monthly[-2]["total_amount"])/monthly[-2]["total_amount"]*100,1)
    return {"revenue":round(revenue,2),"orders":int(len(o)),"customers":int(c.customer_id.nunique()) if not c.empty else 0,"aov":round(revenue/len(o),2) if len(o) else 0,"units":int(i.quantity.sum()) if not i.empty else 0,"growth":growth,"monthly_revenue":monthly}

def product_analytics(db: Session):
    o,c,p,i=frames(db)
    if i.empty or p.empty: return {"top_products":[],"categories":[]}
    j=i.merge(p,on="product_id",how="left")
    top=j.groupby("product_name").agg(revenue=("subtotal","sum"),units=("quantity","sum")).sort_values("revenue",ascending=False).head(10).reset_index().to_dict("records")
    cats=j.groupby("category").subtotal.sum().sort_values(ascending=False).reset_index(name="revenue").to_dict("records")
    return {"top_products":top,"categories":cats}

def customer_analytics(db: Session):
    o,c,p,i=frames(db)
    if o.empty: return {"segments":[],"metrics":{"repeat_rate":0,"avg_spend":0},"rfm":[]}
    rfm=o.groupby("customer_id").agg(last_order=("order_date","max"),frequency=("order_id","nunique"),monetary=("total_amount","sum")).reset_index()
    rfm["recency"]=(o.order_date.max()-rfm.last_order).dt.days
    rfm["segment"]=rfm.apply(lambda x:"Champions" if x.frequency>=4 and x.recency<=30 else "Loyal Customers" if x.frequency>=3 else "Potential Loyalists" if x.frequency==2 and x.recency<=60 else "New Customers" if x.frequency==1 and x.recency<=30 else "At Risk" if x.recency<=90 else "Lost Customers",axis=1)
    seg=rfm.groupby("segment").size().reset_index(name="customers").to_dict("records")
    return {"segments":seg,"metrics":{"repeat_rate":round(float((rfm.frequency>1).mean()*100),1),"avg_spend":round(float(rfm.monetary.mean()),2)},"rfm":rfm.drop(columns="last_order").to_dict("records")}

def insights(db: Session):
    s=summary(db); p=product_analytics(db); c=customer_analytics(db); out=[]
    if p["top_products"]: out.append({"title":"Revenue leader","detail":f"{p['top_products'][0]['product_name']} leads with {p['top_products'][0]['revenue']:,.2f} in recorded revenue."})
    if c["segments"]:
        risk=sum(x["customers"] for x in c["segments"] if x["segment"] in ("At Risk","Lost Customers"))
        out.append({"title":"Retention opportunity","detail":f"{risk} customers are currently classified as at risk or lost."})
    if s["monthly_revenue"]: out.append({"title":"Latest revenue","detail":f"Latest recorded month generated {s['monthly_revenue'][-1]['total_amount']:,.2f}."})
    return out
