from sqlalchemy import Column, BigInteger, String, DECIMAL, TIMESTAMP, Enum as SQLEnum, Index
from sqlalchemy.sql import func
from .database import Base

class Transaction(Base):
    """Transaction model for payment tracking"""
    __tablename__ = "transactions"
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    customer_id = Column(BigInteger, nullable=False, index=True)
    tuition_id = Column(BigInteger, nullable=False, index=True)
    amount = Column(DECIMAL(15, 2), nullable=False)
    status = Column(
        SQLEnum('pending', 'completed', 'cancelled', name='transaction_status'),
        default='pending',
        nullable=False,
        index=True
    )
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp(), nullable=False)
    
    # Composite indexes
    __table_args__ = (
        Index('idx_customer_status', 'customer_id', 'status'),
        Index('idx_created_at', 'created_at'),
    )
    
    def to_dict(self):
        """Convert to dictionary for API response"""
        return {
            "id": self.id,
            "customer_id": self.customer_id,
            "tuition_id": self.tuition_id,
            "amount": float(self.amount),
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
