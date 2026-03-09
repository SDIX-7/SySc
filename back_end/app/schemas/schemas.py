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


class PlanType(str, Enum):
    PROTOTYPE = "prototype"
    PRE_LAUNCH = "pre-launch"
    PRODUCTION = "production"


class ControlPlanStatus(str, Enum):
    DRAFT = "draft"
    APPROVED = "approved"
    ACTIVE = "active"
    OBSOLETE = "obsolete"


class ControlPlanItemBase(BaseModel):
    part_process_number: Optional[str] = None
    process_name: Optional[str] = None
    operation_description: Optional[str] = None
    machine_device_jig_tools: Optional[str] = None
    characteristic_no: Optional[str] = None
    product_characteristic: Optional[str] = None
    process_characteristic: Optional[str] = None
    special_characteristic_class: Optional[str] = None
    specification_tolerance: Optional[str] = None
    evaluation_measurement_technique: Optional[str] = None
    sample_size: Optional[str] = None
    sample_frequency: Optional[str] = None
    control_method: Optional[str] = None
    reaction_plan: Optional[str] = None
    sort_order: int = 0


class ControlPlanItemCreate(ControlPlanItemBase):
    pass


class ControlPlanItemUpdate(ControlPlanItemBase):
    pass


class ControlPlanItemResponse(ControlPlanItemBase):
    id: int
    control_plan_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ControlPlanBase(BaseModel):
    line_id: int
    plan_type: PlanType = PlanType.PRODUCTION
    control_plan_number: Optional[str] = None
    part_number: Optional[str] = None
    latest_change_level: Optional[str] = None
    part_name: Optional[str] = None
    part_description: Optional[str] = None
    organization_plant: Optional[str] = None
    organization_code: Optional[str] = None
    key_contact: Optional[str] = None
    key_contact_phone: Optional[str] = None
    core_team: Optional[str] = None
    org_approval_date: Optional[datetime] = None
    org_approval_by: Optional[str] = None
    other_approval_date: Optional[datetime] = None
    other_approval_by: Optional[str] = None
    date_orig: Optional[datetime] = None
    date_rev: Optional[datetime] = None
    customer_eng_approval_date: Optional[datetime] = None
    customer_eng_approval_by: Optional[str] = None
    customer_quality_approval_date: Optional[datetime] = None
    customer_quality_approval_by: Optional[str] = None
    page_number: Optional[int] = None
    total_pages: Optional[int] = None
    version: str = "1.0"
    status: ControlPlanStatus = ControlPlanStatus.DRAFT
    created_by: Optional[str] = None


class ControlPlanCreate(ControlPlanBase):
    items: Optional[List[ControlPlanItemCreate]] = None


class ControlPlanUpdate(BaseModel):
    plan_type: Optional[PlanType] = None
    control_plan_number: Optional[str] = None
    part_number: Optional[str] = None
    latest_change_level: Optional[str] = None
    part_name: Optional[str] = None
    part_description: Optional[str] = None
    organization_plant: Optional[str] = None
    organization_code: Optional[str] = None
    key_contact: Optional[str] = None
    key_contact_phone: Optional[str] = None
    core_team: Optional[str] = None
    org_approval_date: Optional[datetime] = None
    org_approval_by: Optional[str] = None
    other_approval_date: Optional[datetime] = None
    other_approval_by: Optional[str] = None
    date_orig: Optional[datetime] = None
    date_rev: Optional[datetime] = None
    customer_eng_approval_date: Optional[datetime] = None
    customer_eng_approval_by: Optional[str] = None
    customer_quality_approval_date: Optional[datetime] = None
    customer_quality_approval_by: Optional[str] = None
    page_number: Optional[int] = None
    total_pages: Optional[int] = None
    version: Optional[str] = None
    status: Optional[ControlPlanStatus] = None


class ControlPlanResponse(ControlPlanBase):
    id: int
    created_at: datetime
    updated_at: datetime
    items: Optional[List[ControlPlanItemResponse]] = None

    class Config:
        from_attributes = True


class SignalType(str, Enum):
    POINT_BEYOND_3SIGMA = "point_beyond_3sigma"
    RUN_9 = "run_9"
    TREND_6 = "trend_6"
    ZONE_2OF3 = "zone_2of3"
    ZONE_4OF5 = "zone_4of5"
    RUN_8 = "run_8"
    RUN_6 = "run_6"
    RUN_14 = "run_14"
    RUN_15 = "run_15"


class OCAPPriority(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class OCAPStatus(str, Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    EXECUTING = "executing"
    COMPLETED = "completed"
    CLOSED = "closed"


class OCAPPhase(str, Enum):
    CONTAINMENT = "containment"
    INVESTIGATION = "investigation"
    CORRECTION = "correction"
    VERIFICATION = "verification"


class ActionType(str, Enum):
    IMMEDIATE = "immediate"
    SHORT_TERM = "short_term"
    LONG_TERM = "long_term"


class ExecutionStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    SKIPPED = "skipped"
    FAILED = "failed"


class AnalysisMethod(str, Enum):
    FIVE_WHYS = "5whys"
    FISHBONE = "fishbone"
    PARETO = "pareto"
    FTA = "fta"


class CorrectiveActionType(str, Enum):
    TEMPORARY = "temporary"
    PERMANENT = "permanent"


class CorrectiveActionStatus(str, Enum):
    PLANNED = "planned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    VERIFIED = "verified"


class ProductDisposition(str, Enum):
    RELEASE = "release"
    REWORK = "rework"
    SCRAP = "scrap"
    CONCESSION = "concession"


class OCAPSignalBase(BaseModel):
    signal_time: Optional[datetime] = None
    signal_type: Optional[SignalType] = None
    signal_value: Optional[str] = None
    control_limit_value: Optional[str] = None
    subgroup_index: Optional[int] = None
    raw_data_snapshot: Optional[dict] = None
    chart_snapshot_url: Optional[str] = None
    detected_by: str = "auto"


class OCAPSignalCreate(OCAPSignalBase):
    pass


class OCAPSignalResponse(OCAPSignalBase):
    id: int
    ocap_id: int
    created_at: datetime

    class Config:
        from_attributes = True


class OCAPStepBase(BaseModel):
    phase: OCAPPhase = OCAPPhase.CONTAINMENT
    step_number: int = 1
    action_type: ActionType = ActionType.IMMEDIATE
    action_description: Optional[str] = None
    responsible_role: Optional[str] = None
    responsible_person: Optional[str] = None
    expected_duration_minutes: Optional[int] = None
    deadline: Optional[datetime] = None
    is_mandatory: bool = True
    prerequisites: Optional[List[int]] = None
    sort_order: int = 0


class OCAPStepCreate(OCAPStepBase):
    pass


class OCAPStepUpdate(OCAPStepBase):
    pass


class OCAPStepResponse(OCAPStepBase):
    id: int
    ocap_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class OCAPExecutionBase(BaseModel):
    step_id: Optional[int] = None
    status: ExecutionStatus = ExecutionStatus.PENDING
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    executed_by: Optional[str] = None
    notes: Optional[str] = None
    evidence_urls: Optional[List[str]] = None
    containment_action_taken: Optional[str] = None
    product_disposition: Optional[ProductDisposition] = None


class OCAPExecutionCreate(OCAPExecutionBase):
    pass


class OCAPExecutionUpdate(OCAPExecutionBase):
    pass


class OCAPExecutionResponse(OCAPExecutionBase):
    id: int
    ocap_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class OCAPRootCauseBase(BaseModel):
    analysis_method: AnalysisMethod = AnalysisMethod.FIVE_WHYS
    why_1: Optional[str] = None
    why_2: Optional[str] = None
    why_3: Optional[str] = None
    why_4: Optional[str] = None
    why_5: Optional[str] = None
    fishbone_category: Optional[str] = None
    root_cause_description: Optional[str] = None
    contributing_factors: Optional[List[str]] = None
    evidence_collected: Optional[dict] = None
    verified: bool = False
    verified_by: Optional[str] = None
    verified_at: Optional[datetime] = None


class OCAPRootCauseCreate(OCAPRootCauseBase):
    pass


class OCAPRootCauseUpdate(OCAPRootCauseBase):
    pass


class OCAPRootCauseResponse(OCAPRootCauseBase):
    id: int
    ocap_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class OCAPCorrectiveActionBase(BaseModel):
    root_cause_id: Optional[int] = None
    action_description: Optional[str] = None
    action_type: CorrectiveActionType = CorrectiveActionType.PERMANENT
    responsible_person: Optional[str] = None
    target_date: Optional[datetime] = None
    actual_date: Optional[datetime] = None
    effectiveness_verified: bool = False
    verification_method: Optional[str] = None
    verification_result: Optional[str] = None
    status: CorrectiveActionStatus = CorrectiveActionStatus.PLANNED


class OCAPCorrectiveActionCreate(OCAPCorrectiveActionBase):
    pass


class OCAPCorrectiveActionUpdate(OCAPCorrectiveActionBase):
    pass


class OCAPCorrectiveActionResponse(OCAPCorrectiveActionBase):
    id: int
    ocap_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class OCAPBase(BaseModel):
    control_chart_config_id: Optional[int] = None
    line_id: Optional[int] = None
    name: str
    description: Optional[str] = None
    signal_type: Optional[SignalType] = None
    priority: OCAPPriority = OCAPPriority.MEDIUM
    severity_score: int = 1
    scope_score: int = 1
    trend_score: int = 1
    overall_priority_score: int = 1
    status: OCAPStatus = OCAPStatus.DRAFT
    is_active: bool = True
    created_by: Optional[str] = None


class OCAPCreate(OCAPBase):
    signals: Optional[List[OCAPSignalCreate]] = None
    steps: Optional[List[OCAPStepCreate]] = None


class OCAPUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    signal_type: Optional[SignalType] = None
    priority: Optional[OCAPPriority] = None
    severity_score: Optional[int] = None
    scope_score: Optional[int] = None
    trend_score: Optional[int] = None
    overall_priority_score: Optional[int] = None
    status: Optional[OCAPStatus] = None
    is_active: Optional[bool] = None


class OCAPResponse(OCAPBase):
    id: int
    created_at: datetime
    updated_at: datetime
    signals: Optional[List[OCAPSignalResponse]] = None
    steps: Optional[List[OCAPStepResponse]] = None
    executions: Optional[List[OCAPExecutionResponse]] = None
    root_causes: Optional[List[OCAPRootCauseResponse]] = None
    corrective_actions: Optional[List[OCAPCorrectiveActionResponse]] = None

    class Config:
        from_attributes = True


class MSAStudyType(str, Enum):
    GRR = "grr"
    BIAS = "bias"
    STABILITY = "stability"
    LINEARITY = "linearity"


class MSAStudyStatus(str, Enum):
    DRAFT = "draft"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


class GRRAcceptance(str, Enum):
    ACCEPTABLE = "acceptable"
    CONDITIONAL = "conditional"
    UNACCEPTABLE = "unacceptable"


class NDCAcceptance(str, Enum):
    ACCEPTABLE = "acceptable"
    UNACCEPTABLE = "unacceptable"


class CalculationMethod(str, Enum):
    XR = "xr"
    ANOVA = "anova"


class MSAPartBase(BaseModel):
    part_number: str
    part_name: Optional[str] = None
    reference_value: Optional[str] = None
    sort_order: int = 0


class MSAPartCreate(MSAPartBase):
    pass


class MSAPartUpdate(MSAPartBase):
    pass


class MSAPartResponse(MSAPartBase):
    id: int
    msa_study_id: int

    class Config:
        from_attributes = True


class MSAOperatorBase(BaseModel):
    operator_name: str
    operator_id: Optional[str] = None
    sort_order: int = 0


class MSAOperatorCreate(MSAOperatorBase):
    pass


class MSAOperatorUpdate(MSAOperatorBase):
    pass


class MSAOperatorResponse(MSAOperatorBase):
    id: int
    msa_study_id: int

    class Config:
        from_attributes = True


class MSAMeasurementBase(BaseModel):
    part_id: int
    operator_id: int
    replicate: int = 1
    measurement_value: str
    measurement_order: Optional[int] = None
    measured_at: Optional[datetime] = None


class MSAMeasurementCreate(MSAMeasurementBase):
    pass


class MSAMeasurementUpdate(MSAMeasurementBase):
    pass


class MSAMeasurementResponse(MSAMeasurementBase):
    id: int
    msa_study_id: int

    class Config:
        from_attributes = True


class MSAResultBase(BaseModel):
    study_type: MSAStudyType = MSAStudyType.GRR
    calculation_method: CalculationMethod = CalculationMethod.XR

    variance_repeatability: Optional[str] = None
    variance_reproducibility: Optional[str] = None
    variance_grr: Optional[str] = None
    variance_part: Optional[str] = None
    variance_total: Optional[str] = None

    stddev_repeatability: Optional[str] = None
    stddev_reproducibility: Optional[str] = None
    stddev_grr: Optional[str] = None
    stddev_part: Optional[str] = None
    stddev_total: Optional[str] = None

    percent_grr: Optional[str] = None
    percent_tolerance: Optional[str] = None
    ndc: Optional[str] = None

    grr_acceptance: Optional[GRRAcceptance] = None
    ndc_acceptance: Optional[NDCAcceptance] = None
    overall_acceptance: Optional[GRRAcceptance] = None


class MSAResultResponse(MSAResultBase):
    id: int
    msa_study_id: int
    detailed_results: Optional[dict] = None
    calculated_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True


class MSAStudyBase(BaseModel):
    line_id: Optional[int] = None
    study_name: str
    study_type: MSAStudyType = MSAStudyType.GRR
    status: MSAStudyStatus = MSAStudyStatus.DRAFT
    measurement_system: Optional[str] = None
    characteristic: Optional[str] = None
    specification_lower: Optional[str] = None
    specification_upper: Optional[str] = None
    specification_target: Optional[str] = None
    tolerance: Optional[str] = None
    number_of_parts: int = 10
    number_of_operators: int = 3
    number_of_replicates: int = 3
    random_order: bool = False
    created_by: Optional[str] = None


class MSAStudyCreate(MSAStudyBase):
    parts: Optional[List[MSAPartBase]] = None
    operators: Optional[List[MSAOperatorBase]] = None
    measurements: Optional[List[MSAMeasurementBase]] = None


class MSAStudyUpdate(BaseModel):
    study_name: Optional[str] = None
    study_type: Optional[MSAStudyType] = None
    status: Optional[MSAStudyStatus] = None
    measurement_system: Optional[str] = None
    characteristic: Optional[str] = None
    specification_lower: Optional[str] = None
    specification_upper: Optional[str] = None
    specification_target: Optional[str] = None
    tolerance: Optional[str] = None
    number_of_parts: Optional[int] = None
    number_of_operators: Optional[int] = None
    number_of_replicates: Optional[int] = None
    random_order: Optional[bool] = None


class MSAStudyResponse(MSAStudyBase):
    id: int
    created_at: datetime
    updated_at: datetime
    parts: Optional[List[MSAPartResponse]] = None
    operators: Optional[List[MSAOperatorResponse]] = None
    measurements: Optional[List[MSAMeasurementResponse]] = None
    result: Optional[MSAResultResponse] = None

    class Config:
        from_attributes = True
