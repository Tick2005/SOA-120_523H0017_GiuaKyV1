from sqlalchemy import Column, BigInteger, String, Integer, Numeric, Enum, TIMESTAMP, func
from .database import Base
import enum

class TuitionStatus(str, enum.Enum):
    """Enum for tuition status"""
    UNPAID = "unpaid"
    PAID = "paid"

class Tuition(Base):
    """Tuition model - merged students and tuitions into single table"""
    __tablename__ = "tuitions"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    student_id = Column(String(20), nullable=False, index=True)
    student_name = Column(String(100), nullable=False)
    student_email = Column(String(100), nullable=False, index=True)
    semester = Column(Integer, nullable=False)  # 1, 2, 3
    academic_year = Column(String(20), nullable=False)  # "2024-2025"
    fee = Column(Numeric(15, 2), nullable=False)
    status = Column(Enum('unpaid', 'paid', name='tuitionstatus'), default='unpaid', nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp())
    updated_at = Column(
        TIMESTAMP, 
        server_default=func.current_timestamp(),
        onupdate=func.current_timestamp()
    )

    def to_dict(self, include_can_pay=False):
        """Convert to dictionary for API response"""
        data = {
            "id": self.id,
            "student_id": self.student_id,
            "semester": self.semester,
            "academic_year": self.academic_year,
            "fee": float(self.fee),
            "status": self.status  # Already a string now
        }
        if include_can_pay:
            data["canPay"] = False  # Will be set to True for the first unpaid tuition
        return data
