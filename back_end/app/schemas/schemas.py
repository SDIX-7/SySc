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


class DataType(str, Enum):
    MEASUREMENT = "measurement"
    ATTRIBUTE = "attribute"


class LineStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"


class ProductionLineCreate(BaseModel):
    line_code: str
    line_name: str
    line_description: Optional[str] = None
    data_type: DataType = DataType.ATTRIBUTE
    model_path: Optional[str] = None
    status: LineStatus = LineStatus.ACTIVE


class ProductionLineUpdate(BaseModel):
    line_name: Optional[str] = None
    line_description: Optional[str] = None
    data_type: Optional[DataType] = None
    model_path: Optional[str] = None
    status: Optional[LineStatus] = None


class ProductionLineResponse(BaseModel):
    id: int
    line_code: str
    line_name: str
    line_description: Optional[str]
    data_type: str
    model_path: Optional[str]
    status: str
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


class MeasurementDataCreate(BaseModel):
    line_id: int
    sample_id: str
    measurement_values: List[float]
    measurement_time: Optional[str] = None
    operator: Optional[str] = None
    equipment: Optional[str] = None


class MeasurementDataResponse(BaseModel):
    id: int
    line_id: int
    sample_id: str
    measurement_values: List[float]
    measurement_time: datetime
    operator: Optional[str]
    equipment: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class AttributeDataCreate(BaseModel):
    line_id: int
    sample_id: str
    sample_size: int
    defect_count: int = 0
    defect_details: Optional[dict] = {}
    inspection_time: Optional[str] = None
    inspector: Optional[str] = None


class AttributeDataResponse(BaseModel):
    id: int
    line_id: int
    sample_id: str
    sample_size: int
    defect_count: int
    defect_details: dict
    inspection_time: datetime
    inspector: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class ControlChartType(str, Enum):
    XR = "XR"
    XS = "XS"
    P = "P"
    NP = "NP"
    C = "C"
    U = "U"


class ControlLimitType(str, Enum):
    FIXED = "fixed"
    DYNAMIC = "dynamic"
    CUSTOM = "custom"


class ControlChartConfigCreate(BaseModel):
    line_id: int
    chart_type: ControlChartType = ControlChartType.U
    control_limit_type: ControlLimitType = ControlLimitType.DYNAMIC
    alarm_rules: Optional[List] = []


class ControlChartConfigUpdate(BaseModel):
    chart_type: Optional[ControlChartType] = None
    control_limit_type: Optional[ControlLimitType] = None
    alarm_rules: Optional[List] = None


class ControlChartConfigResponse(BaseModel):
    id: int
    line_id: int
    chart_type: str
    control_limit_type: str
    alarm_rules: List
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


class SamplingType(str, Enum):
    SINGLE = "single"
    DOUBLE = "double"
    MULTIPLE = "multiple"


class InspectionLevel(str, Enum):
    S1 = "S-1"
    S2 = "S-2"
    S3 = "S-3"
    S4 = "S-4"
    I = "I"
    II = "II"
    III = "III"


class SamplingPlanCreate(BaseModel):
    line_id: Optional[int] = None
    plan_name: str
    batch_size: int
    aql_value: str = "1.0"
    inspection_level: InspectionLevel = InspectionLevel.II
    sampling_type: SamplingType = SamplingType.SINGLE


class SamplingPlanResponse(BaseModel):
    id: int
    line_id: Optional[int]
    plan_name: str
    batch_size: int
    aql_value: str
    inspection_level: str
    sample_size: Optional[int]
    acceptance_number: Optional[int]
    rejection_number: Optional[int]
    sampling_type: str
    created_at: datetime

    class Config:
        from_attributes = True


class SamplingRecordCreate(BaseModel):
    plan_id: Optional[int] = None
    line_id: Optional[int] = None
    batch_id: str
    sample_size: int
    defect_count: int = 0
    judgment: Optional[str] = None
    inspection_status: Optional[str] = "normal"


class SamplingRecordResponse(BaseModel):
    id: int
    plan_id: Optional[int]
    line_id: Optional[int]
    batch_id: str
    sample_size: int
    defect_count: int
    judgment: Optional[str]
    inspection_status: str
    created_at: datetime

    class Config:
        from_attributes = True


class AnalysisType(str, Enum):
    PROCESS = "process"
    MACHINE = "machine"
    PRELIMINARY = "preliminary"


class CapabilityAnalysisCreate(BaseModel):
    line_id: int
    analysis_name: Optional[str] = None
    usl: float
    lsl: float
    target: Optional[float] = None
    sigma_machine: Optional[float] = None
    data_values: List[float]
    analysis_type: AnalysisType = AnalysisType.PROCESS


class CapabilityAnalysisResponse(BaseModel):
    id: int
    line_id: int
    analysis_name: Optional[str]
    usl: str
    lsl: str
    target: Optional[str]
    cp: Optional[str]
    cpk: Optional[str]
    pp: Optional[str]
    ppk: Optional[str]
    cm: Optional[str]
    cmk: Optional[str]
    mean: Optional[str]
    sigma_within: Optional[str]
    sigma_overall: Optional[str]
    sigma_machine: Optional[str]
    sample_count: int
    subgroup_count: int
    data_values: List
    status: str
    analysis_type: str
    analysis_time: datetime
    created_at: datetime

    class Config:
        from_attributes = True
