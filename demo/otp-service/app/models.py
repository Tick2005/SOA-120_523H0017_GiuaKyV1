from sqlalchemy import Column, BigInteger, String, Integer, TIMESTAMP, Enum as SQLEnum, Index
from sqlalchemy.sql import func
from .database import Base

class OTP(Base):
    """OTP model for verification"""
    __tablename__ = "otp"
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    otp_code = Column(String(6), nullable=False, index=True)
    transaction_id = Column(BigInteger, unique=True, nullable=False, index=True)
    status = Column(
        SQLEnum('active', 'used', 'expired', name='otp_status'),
        default='active',
        nullable=False,
        index=True
    )
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp(), nullable=False, index=True)
    
    # Composite indexes
    __table_args__ = (
        Index('idx_otp_code_status', 'otp_code', 'status'),
        Index('idx_status_created', 'status', 'created_at'),
    )
    
    def to_dict(self):
        """Convert to dictionary for API response"""
        return {
            "id": self.id,
            "otp_code": self.otp_code,
            "transaction_id": self.transaction_id,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
