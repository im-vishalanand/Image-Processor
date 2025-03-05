# --- models.py (Database models) ---
from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class Request(Base):
    __tablename__ = "requests"

    id = Column(Integer, primary_key=True, index=True)
    request_id = Column(String(255), unique=True, nullable=False)
    status = Column(String(50), default="processing")

    # Relationship with images (Cascade delete when request is deleted)
    images = relationship("Image", back_populates="request", cascade="all, delete-orphan")


class Image(Base):
    __tablename__ = "images"

    id = Column(Integer, primary_key=True, index=True)
    request_id = Column(String(255), ForeignKey("requests.request_id", ondelete="CASCADE"))
    product_name = Column(String(255), nullable=False)
    input_url = Column(String(2083), nullable=False)
    output_url = Column(String(2083), nullable=True)
    status = Column(String(50), default="pending")

    # Relationship back to request
    request = relationship("Request", back_populates="images")
