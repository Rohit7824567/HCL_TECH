from sqlalchemy import Column, Integer, String, Float, Date, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database.db import Base

class Customer(Base):
    __tablename__ = "customers"
    id = Column(Integer, primary_key=True)
    customer_id = Column(String(100), unique=True, index=True, nullable=False)
    customer_name = Column(String(200), nullable=False)
    email = Column(String(255))
    gender = Column(String(40))
    age = Column(Integer)
    city = Column(String(120))
    registration_date = Column(Date)
    orders = relationship("Order", back_populates="customer")

class Product(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True)
    product_id = Column(String(100), unique=True, index=True, nullable=False)
    product_name = Column(String(240), nullable=False)
    category = Column(String(120), index=True)
    unit_price = Column(Float, nullable=False)
    description = Column(String(500))
    items = relationship("OrderItem", back_populates="product")

class Order(Base):
    __tablename__ = "orders"
    id = Column(Integer, primary_key=True)
    order_id = Column(String(120), unique=True, index=True, nullable=False)
    customer_id = Column(String(100), ForeignKey("customers.customer_id"), index=True, nullable=False)
    order_date = Column(Date, index=True, nullable=False)
    total_amount = Column(Float, nullable=False)
    payment_method = Column(String(80))
    order_status = Column(String(40), default="Completed")
    customer = relationship("Customer", back_populates="orders")
    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")

class OrderItem(Base):
    __tablename__ = "order_items"
    id = Column(Integer, primary_key=True)
    item_id = Column(String(150), unique=True, index=True, nullable=False)
    order_id = Column(String(120), ForeignKey("orders.order_id"), index=True, nullable=False)
    product_id = Column(String(100), ForeignKey("products.product_id"), index=True, nullable=False)
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Float, nullable=False)
    subtotal = Column(Float, nullable=False)
    order = relationship("Order", back_populates="items")
    product = relationship("Product", back_populates="items")

class DataImport(Base):
    __tablename__ = "data_imports"
    id = Column(Integer, primary_key=True)
    file_name = Column(String(255), nullable=False)
    upload_date = Column(DateTime, default=datetime.utcnow)
    total_records = Column(Integer, default=0)
    successful_records = Column(Integer, default=0)
    failed_records = Column(Integer, default=0)
    import_status = Column(String(40), default="completed")

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    full_name = Column(String(200), nullable=False)
    password_hash = Column(String(300), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

Index("ix_order_date_customer", Order.order_date, Order.customer_id)
