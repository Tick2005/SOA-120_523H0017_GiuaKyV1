from sqlalchemy import Column, BigInteger, String, DECIMAL, Index
from .database import Base

class Customer(Base):
    __tablename__ = "customers"
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password = Column(String(255), nullable=False)  # Plain text password
    full_name = Column(String(100), nullable=False)  # Full name of customer
    phone_number = Column(String(20), nullable=False)  # Phone number
    balance = Column(DECIMAL(15, 2), nullable=False, default=0)
    
    # Indexes
    __table_args__ = (
        Index('idx_username', 'username'),
        Index('idx_email', 'email'),
    )
