from sqlalchemy import Column, Integer, String, Boolean, Text, DateTime
from sqlalchemy.sql import func
from datetime import datetime
from ..database import Base
import json


class Image(Base):
    __tablename__ = "image"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    hasDefects = Column(Boolean, default=False)
    detection_total_cnts = Column(Integer, default=0)
    detection_classes = Column(Text, default="[]")
    detection_boxes = Column(Text, default="[]")
    detection_scores = Column(Text, default="[]")
    captureTime = Column(DateTime, default=datetime.now)

    def get_detection_classes(self) -> list:
        try:
            return json.loads(self.detection_classes) if self.detection_classes else []
        except:
            return []

    def get_detection_boxes(self) -> list:
        try:
            return json.loads(self.detection_boxes) if self.detection_boxes else []
        except:
            return []

    def get_detection_scores(self) -> list:
        try:
            return json.loads(self.detection_scores) if self.detection_scores else []
        except:
            return []

    def set_detection_classes(self, value: list):
        self.detection_classes = json.dumps(value)

    def set_detection_boxes(self, value: list):
        self.detection_boxes = json.dumps(value)

    def set_detection_scores(self, value: list):
        self.detection_scores = json.dumps(value)


class EmailSettings(Base):
    __tablename__ = "email_settings"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(100), nullable=False)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)


class User(Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(50), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    name = Column(String(100), nullable=False)
    role = Column(String(20), nullable=False)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
