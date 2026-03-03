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


class ProductionLine(Base):
    __tablename__ = "production_line"

    id = Column(Integer, primary_key=True, index=True)
    line_code = Column(String(50), unique=True, nullable=False)
    line_name = Column(String(100), nullable=False)
    line_description = Column(String(500), nullable=True)
    data_type = Column(String(20), default="attribute")
    model_path = Column(String(255), nullable=True)
    status = Column(String(20), default="active")
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)


class MeasurementData(Base):
    __tablename__ = "measurement_data"

    id = Column(Integer, primary_key=True, index=True)
    line_id = Column(Integer, nullable=False)
    sample_id = Column(String(100), nullable=False)
    measurement_values = Column(Text, default="[]")
    measurement_time = Column(DateTime, default=datetime.now)
    operator = Column(String(100), nullable=True)
    equipment = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.now)

    def get_measurement_values(self) -> list:
        try:
            return json.loads(self.measurement_values) if self.measurement_values else []
        except:
            return []

    def set_measurement_values(self, value: list):
        self.measurement_values = json.dumps(value)


class AttributeData(Base):
    __tablename__ = "attribute_data"

    id = Column(Integer, primary_key=True, index=True)
    line_id = Column(Integer, nullable=False)
    sample_id = Column(String(100), nullable=False)
    sample_size = Column(Integer, default=0)
    defect_count = Column(Integer, default=0)
    defect_details = Column(Text, default="{}")
    inspection_time = Column(DateTime, default=datetime.now)
    inspector = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.now)

    def get_defect_details(self) -> dict:
        try:
            return json.loads(self.defect_details) if self.defect_details else {}
        except:
            return {}

    def set_defect_details(self, value: dict):
        self.defect_details = json.dumps(value)


class ControlChartConfig(Base):
    __tablename__ = "control_chart_config"

    id = Column(Integer, primary_key=True, index=True)
    line_id = Column(Integer, nullable=False)
    chart_type = Column(String(20), default="U")
    control_limit_type = Column(String(20), default="dynamic")
    alarm_rules = Column(Text, default="[]")
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    def get_alarm_rules(self) -> list:
        try:
            return json.loads(self.alarm_rules) if self.alarm_rules else []
        except:
            return []

    def set_alarm_rules(self, value: list):
        self.alarm_rules = json.dumps(value)


class SamplingPlan(Base):
    __tablename__ = "sampling_plan"

    id = Column(Integer, primary_key=True, index=True)
    line_id = Column(Integer, nullable=True)
    plan_name = Column(String(100), nullable=False)
    batch_size = Column(Integer, nullable=False)
    aql_value = Column(String(20), default="1.0")
    inspection_level = Column(String(10), default="II")
    sample_size = Column(Integer, nullable=True)
    acceptance_number = Column(Integer, nullable=True)
    rejection_number = Column(Integer, nullable=True)
    sampling_type = Column(String(20), default="single")
    created_at = Column(DateTime, default=datetime.now)


class SamplingRecord(Base):
    __tablename__ = "sampling_record"

    id = Column(Integer, primary_key=True, index=True)
    plan_id = Column(Integer, nullable=True)
    line_id = Column(Integer, nullable=True)
    batch_id = Column(String(100), nullable=False)
    sample_size = Column(Integer, nullable=False)
    defect_count = Column(Integer, default=0)
    judgment = Column(String(20), nullable=True)
    inspection_status = Column(String(20), default="normal")
    created_at = Column(DateTime, default=datetime.now)


class CapabilityAnalysis(Base):
    __tablename__ = "capability_analysis"

    id = Column(Integer, primary_key=True, index=True)
    line_id = Column(Integer, nullable=False)
    analysis_name = Column(String(100), nullable=True)
    usl = Column(String(50), nullable=False)
    lsl = Column(String(50), nullable=False)
    target = Column(String(50), nullable=True)
    cp = Column(String(50), nullable=True)
    cpk = Column(String(50), nullable=True)
    pp = Column(String(50), nullable=True)
    ppk = Column(String(50), nullable=True)
    cm = Column(String(50), nullable=True)
    cmk = Column(String(50), nullable=True)
    mean = Column(String(50), nullable=True)
    sigma_within = Column(String(50), nullable=True)
    sigma_overall = Column(String(50), nullable=True)
    sigma_machine = Column(String(50), nullable=True)
    sample_count = Column(Integer, default=0)
    subgroup_count = Column(Integer, default=0)
    data_values = Column(Text, default="[]")
    status = Column(String(20), default="completed")
    analysis_type = Column(String(20), default="process")
    analysis_time = Column(DateTime, default=datetime.now)
    created_at = Column(DateTime, default=datetime.now)

    def get_data_values(self) -> list:
        try:
            return json.loads(self.data_values) if self.data_values else []
        except:
            return []

    def set_data_values(self, value: list):
        self.data_values = json.dumps(value)
