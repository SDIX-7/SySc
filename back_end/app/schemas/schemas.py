from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List
from datetime import datetime
from enum import Enum


class UserRole(str, Enum):
    ADMIN = "admin"
    DETECTOR = "detector"
    MONITOR = "monitor"


class ImageResponse(BaseModel):
    id: int
    name: str
    hasDefects: bool
    detection_total_cnts: int = 0
    detection_classes: List[str] = []
    detection_boxes: List[List[float]] = []
    detection_scores: List[float] = []
    captureTime: datetime

    class Config:
        from_attributes = True


class ImageCreate(BaseModel):
    name: str
    hasDefects: bool
    captureTime: str
    detection_total_cnts: int = 0
    detection_classes: List[str] = []
    detection_boxes: List[List[float]] = []
    detection_scores: List[float] = []


class DetectionResultCreate(BaseModel):
    name: str
    hasDefects: bool
    captureTime: str
    detection_total_cnts: int = 0
    detection_classes: List[str] = []
    detection_boxes: List[List[float]] = []
    detection_scores: List[float] = []


class EmailSettingsResponse(BaseModel):
    email: str
    updated_at: datetime

    class Config:
        from_attributes = True


class EmailSettingsUpdate(BaseModel):
    email: EmailStr


class UserCreate(BaseModel):
    user_id: str
    password: str
    name: str
    role: UserRole


class UserResponse(BaseModel):
    id: int
    user_id: str
    name: str
    role: str
    created_at: datetime

    class Config:
        from_attributes = True


class MessageResponse(BaseModel):
    message: str
