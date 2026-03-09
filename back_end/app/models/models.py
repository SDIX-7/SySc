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


class ControlPlan(Base):
    __tablename__ = "control_plan"

    id = Column(Integer, primary_key=True, index=True)
    line_id = Column(Integer, nullable=False, index=True)
    plan_type = Column(String(20), nullable=False, default="production")
    control_plan_number = Column(String(100), nullable=True)
    part_number = Column(String(100), nullable=True)
    latest_change_level = Column(String(100), nullable=True)
    name = Column(String(200), nullable=True)
    part_name = Column(String(200), nullable=True)
    part_description = Column(String(500), nullable=True)
    organization_plant = Column(String(200), nullable=True)
    organization_code = Column(String(100), nullable=True)
    key_contact = Column(String(200), nullable=True)
    key_contact_phone = Column(String(50), nullable=True)
    core_team = Column(Text, nullable=True)
    org_approval_date = Column(DateTime, nullable=True)
    org_approval_by = Column(String(100), nullable=True)
    other_approval_date = Column(DateTime, nullable=True)
    other_approval_by = Column(String(100), nullable=True)
    date_orig = Column(DateTime, nullable=True)
    date_rev = Column(DateTime, nullable=True)
    customer_eng_approval_date = Column(DateTime, nullable=True)
    customer_eng_approval_by = Column(String(100), nullable=True)
    customer_quality_approval_date = Column(DateTime, nullable=True)
    customer_quality_approval_by = Column(String(100), nullable=True)
    page_number = Column(Integer, nullable=True)
    total_pages = Column(Integer, nullable=True)
    version = Column(String(20), default="1.0")
    status = Column(String(20), default="draft")
    created_by = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)


class ControlPlanItem(Base):
    __tablename__ = "control_plan_item"

    id = Column(Integer, primary_key=True, index=True)
    control_plan_id = Column(Integer, nullable=False, index=True)
    part_process_number = Column(String(50), nullable=True)
    process_name = Column(String(200), nullable=True)
    operation_description = Column(String(500), nullable=True)
    machine_device_jig_tools = Column(String(500), nullable=True)
    characteristic_no = Column(String(50), nullable=True)
    product_characteristic = Column(String(500), nullable=True)
    process_characteristic = Column(String(500), nullable=True)
    special_characteristic_class = Column(String(20), nullable=True)
    specification_tolerance = Column(String(500), nullable=True)
    evaluation_measurement_technique = Column(String(500), nullable=True)
    sample_size = Column(String(50), nullable=True)
    sample_frequency = Column(String(100), nullable=True)
    control_method = Column(String(500), nullable=True)
    reaction_plan = Column(String(1000), nullable=True)
    sort_order = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)


class OCAP(Base):
    __tablename__ = "ocap"

    id = Column(Integer, primary_key=True, index=True)
    control_chart_config_id = Column(Integer, nullable=True, index=True)
    line_id = Column(Integer, nullable=True, index=True)
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    signal_type = Column(String(50), nullable=True)
    priority = Column(String(20), default="medium")
    severity_score = Column(Integer, default=1)
    scope_score = Column(Integer, default=1)
    trend_score = Column(Integer, default=1)
    overall_priority_score = Column(Integer, default=1)
    status = Column(String(20), default="draft")
    is_active = Column(Boolean, default=True)
    created_by = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)


class OCAPSignal(Base):
    __tablename__ = "ocap_signal"

    id = Column(Integer, primary_key=True, index=True)
    ocap_id = Column(Integer, nullable=False, index=True)
    signal_time = Column(DateTime, default=datetime.now)
    signal_type = Column(String(50), nullable=True)
    signal_value = Column(String(100), nullable=True)
    control_limit_value = Column(String(100), nullable=True)
    subgroup_index = Column(Integer, nullable=True)
    raw_data_snapshot = Column(Text, nullable=True)
    chart_snapshot_url = Column(String(500), nullable=True)
    detected_by = Column(String(20), default="auto")
    created_at = Column(DateTime, default=datetime.now)

    def get_raw_data_snapshot(self) -> dict:
        try:
            return json.loads(self.raw_data_snapshot) if self.raw_data_snapshot else {}
        except:
            return {}

    def set_raw_data_snapshot(self, value: dict):
        self.raw_data_snapshot = json.dumps(value)


class OCAPStep(Base):
    __tablename__ = "ocap_step"

    id = Column(Integer, primary_key=True, index=True)
    ocap_id = Column(Integer, nullable=False, index=True)
    phase = Column(String(30), default="containment")
    step_number = Column(Integer, default=1)
    action_type = Column(String(30), default="immediate")
    action_description = Column(Text, nullable=True)
    responsible_role = Column(String(100), nullable=True)
    responsible_person = Column(String(100), nullable=True)
    expected_duration_minutes = Column(Integer, nullable=True)
    deadline = Column(DateTime, nullable=True)
    is_mandatory = Column(Boolean, default=True)
    prerequisites = Column(Text, nullable=True)
    sort_order = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    def get_prerequisites(self) -> list:
        try:
            return json.loads(self.prerequisites) if self.prerequisites else []
        except:
            return []

    def set_prerequisites(self, value: list):
        self.prerequisites = json.dumps(value)


class OCAPExecution(Base):
    __tablename__ = "ocap_execution"

    id = Column(Integer, primary_key=True, index=True)
    ocap_id = Column(Integer, nullable=False, index=True)
    step_id = Column(Integer, nullable=True, index=True)
    status = Column(String(20), default="pending")
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    executed_by = Column(String(100), nullable=True)
    notes = Column(Text, nullable=True)
    evidence_urls = Column(Text, nullable=True)
    containment_action_taken = Column(Text, nullable=True)
    product_disposition = Column(String(30), nullable=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    def get_evidence_urls(self) -> list:
        try:
            return json.loads(self.evidence_urls) if self.evidence_urls else []
        except:
            return []

    def set_evidence_urls(self, value: list):
        self.evidence_urls = json.dumps(value)


class OCAPRootCause(Base):
    __tablename__ = "ocap_root_cause"

    id = Column(Integer, primary_key=True, index=True)
    ocap_id = Column(Integer, nullable=False, index=True)
    analysis_method = Column(String(30), default="5whys")
    why_1 = Column(Text, nullable=True)
    why_2 = Column(Text, nullable=True)
    why_3 = Column(Text, nullable=True)
    why_4 = Column(Text, nullable=True)
    why_5 = Column(Text, nullable=True)
    fishbone_category = Column(String(50), nullable=True)
    root_cause_description = Column(Text, nullable=True)
    contributing_factors = Column(Text, nullable=True)
    evidence_collected = Column(Text, nullable=True)
    verified = Column(Boolean, default=False)
    verified_by = Column(String(100), nullable=True)
    verified_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    def get_contributing_factors(self) -> list:
        try:
            return json.loads(self.contributing_factors) if self.contributing_factors else []
        except:
            return []

    def set_contributing_factors(self, value: list):
        self.contributing_factors = json.dumps(value)

    def get_evidence_collected(self) -> dict:
        try:
            return json.loads(self.evidence_collected) if self.evidence_collected else {}
        except:
            return {}

    def set_evidence_collected(self, value: dict):
        self.evidence_collected = json.dumps(value)


class OCAPCorrectiveAction(Base):
    __tablename__ = "ocap_corrective_action"

    id = Column(Integer, primary_key=True, index=True)
    ocap_id = Column(Integer, nullable=False, index=True)
    root_cause_id = Column(Integer, nullable=True, index=True)
    action_description = Column(Text, nullable=True)
    action_type = Column(String(20), default="permanent")
    responsible_person = Column(String(100), nullable=True)
    target_date = Column(DateTime, nullable=True)
    actual_date = Column(DateTime, nullable=True)
    effectiveness_verified = Column(Boolean, default=False)
    verification_method = Column(String(200), nullable=True)
    verification_result = Column(Text, nullable=True)
    status = Column(String(20), default="planned")
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)


class MSAStudy(Base):
    __tablename__ = "msa_study"

    id = Column(Integer, primary_key=True, index=True)
    line_id = Column(Integer, nullable=True, index=True)
    study_name = Column(String(200), nullable=False)
    study_type = Column(String(20), default="grr")
    status = Column(String(20), default="draft")
    measurement_system = Column(String(500), nullable=True)
    characteristic = Column(String(200), nullable=True)
    specification_lower = Column(String(50), nullable=True)
    specification_upper = Column(String(50), nullable=True)
    specification_target = Column(String(50), nullable=True)
    tolerance = Column(String(50), nullable=True)
    number_of_parts = Column(Integer, default=10)
    number_of_operators = Column(Integer, default=3)
    number_of_replicates = Column(Integer, default=3)
    random_order = Column(Boolean, default=False)
    created_by = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)


class MSAPart(Base):
    __tablename__ = "msa_part"

    id = Column(Integer, primary_key=True, index=True)
    msa_study_id = Column(Integer, nullable=False, index=True)
    part_number = Column(String(100), nullable=False)
    part_name = Column(String(200), nullable=True)
    reference_value = Column(String(50), nullable=True)
    sort_order = Column(Integer, default=0)


class MSAOperator(Base):
    __tablename__ = "msa_operator"

    id = Column(Integer, primary_key=True, index=True)
    msa_study_id = Column(Integer, nullable=False, index=True)
    operator_name = Column(String(100), nullable=False)
    operator_id = Column(String(50), nullable=True)
    sort_order = Column(Integer, default=0)


class MSAMeasurement(Base):
    __tablename__ = "msa_measurement"

    id = Column(Integer, primary_key=True, index=True)
    msa_study_id = Column(Integer, nullable=False, index=True)
    part_id = Column(Integer, nullable=False, index=True)
    operator_id = Column(Integer, nullable=False, index=True)
    replicate = Column(Integer, default=1)
    measurement_value = Column(String(50), nullable=False)
    measurement_order = Column(Integer, nullable=True)
    measured_at = Column(DateTime, nullable=True)


class MSAResult(Base):
    __tablename__ = "msa_result"

    id = Column(Integer, primary_key=True, index=True)
    msa_study_id = Column(Integer, nullable=False, index=True)
    study_type = Column(String(20), default="grr")
    calculation_method = Column(String(20), default="xr")

    variance_repeatability = Column(String(50), nullable=True)
    variance_reproducibility = Column(String(50), nullable=True)
    variance_grr = Column(String(50), nullable=True)
    variance_part = Column(String(50), nullable=True)
    variance_total = Column(String(50), nullable=True)

    stddev_repeatability = Column(String(50), nullable=True)
    stddev_reproducibility = Column(String(50), nullable=True)
    stddev_grr = Column(String(50), nullable=True)
    stddev_part = Column(String(50), nullable=True)
    stddev_total = Column(String(50), nullable=True)

    percent_grr = Column(String(50), nullable=True)
    percent_tolerance = Column(String(50), nullable=True)
    ndc = Column(String(50), nullable=True)

    grr_acceptance = Column(String(20), nullable=True)
    ndc_acceptance = Column(String(20), nullable=True)
    overall_acceptance = Column(String(20), nullable=True)

    detailed_results = Column(Text, nullable=True)

    calculated_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.now)

    def get_detailed_results(self) -> dict:
        try:
            return json.loads(self.detailed_results) if self.detailed_results else {}
        except:
            return {}

    def set_detailed_results(self, value: dict):
        self.detailed_results = json.dumps(value)
