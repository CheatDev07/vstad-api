from sqlalchemy import Column, Integer, String, DateTime, Float, ForeignKey, Boolean, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base

class Video(Base):
    __tablename__ = "videos"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(String(1000), nullable=True)
    uploader_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # File info
    file_name = Column(String(255), nullable=False)
    file_size = Column(Integer, nullable=False)  # in bytes
    file_path = Column(String(500), nullable=False)  # MinIO path
    video_url = Column(Text)
    
    # Video metadata
    duration = Column(Float, nullable=True)  # in seconds
    width = Column(Integer, nullable=True)
    height = Column(Integer, nullable=True)
    fps = Column(Float, nullable=True)
    codec = Column(String(50), nullable=True)
    
    # Processing
    is_processing = Column(Boolean, default=False)
    is_processed = Column(Boolean, default=False)
    thumbnail_path = Column(String(500), nullable=True)
    
    # Status
    view_count = Column(Integer, default=0)
    like_count = Column(Integer, default=0)
    comment_count = Column(Integer, default=0)  # Add comment count
    share_count = Column(Integer, default=0)  # Add share count
    is_public = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    uploader = relationship("User", back_populates="videos")
    like_list = relationship("Like", back_populates="video", cascade="all, delete-orphan")
    comment_list = relationship("Comment", back_populates="video", cascade="all, delete-orphan")
    share_list = relationship("Share", back_populates="video", cascade="all, delete-orphan")
    favorite_list = relationship("Favorite", back_populates="video", cascade="all, delete-orphan")
