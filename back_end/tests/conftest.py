import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app

SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db_session():
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def sample_production_line():
    return {
        "line_code": "TEST-LINE-001",
        "line_name": "测试产线",
        "line_description": "用于测试的产线",
        "data_type": "attribute",
        "status": "active"
    }


@pytest.fixture
def sample_control_chart_config():
    return {
        "line_id": 1,
        "chart_type": "U",
        "control_limit_type": "dynamic",
        "alarm_rules": []
    }


@pytest.fixture
def sample_ocap():
    return {
        "name": "测试OCAP",
        "description": "这是一个测试OCAP",
        "signal_type": "point_beyond_3sigma",
        "priority": "high",
        "severity_score": 8,
        "scope_score": 7,
        "trend_score": 6,
        "overall_priority_score": 7,
        "status": "draft",
        "is_active": True,
        "created_by": "测试用户"
    }


@pytest.fixture
def sample_ocap_with_nested():
    return {
        "name": "带嵌套数据的OCAP",
        "description": "包含Signal和Step的OCAP",
        "signal_type": "run_9",
        "priority": "critical",
        "severity_score": 9,
        "scope_score": 8,
        "trend_score": 7,
        "overall_priority_score": 8,
        "status": "active",
        "is_active": True,
        "created_by": "测试用户",
        "signals": [
            {
                "signal_time": "2026-03-07T10:00:00",
                "signal_type": "run_9",
                "signal_value": "0.85",
                "control_limit_value": "0.50",
                "subgroup_index": 15,
                "raw_data_snapshot": {"data": [1, 2, 3]},
                "detected_by": "auto"
            }
        ],
        "steps": [
            {
                "phase": "containment",
                "step_number": 1,
                "action_type": "immediate",
                "action_description": "停止生产并隔离产品",
                "responsible_role": "操作员",
                "responsible_person": "张三",
                "expected_duration_minutes": 30,
                "is_mandatory": True,
                "sort_order": 1
            },
            {
                "phase": "investigation",
                "step_number": 2,
                "action_type": "short_term",
                "action_description": "进行根本原因分析",
                "responsible_role": "质量工程师",
                "responsible_person": "李四",
                "expected_duration_minutes": 120,
                "is_mandatory": True,
                "prerequisites": [1],
                "sort_order": 2
            }
        ]
    }


@pytest.fixture
def sample_ocap_signal():
    return {
        "signal_time": "2026-03-07T10:00:00",
        "signal_type": "point_beyond_3sigma",
        "signal_value": "0.95",
        "control_limit_value": "0.50",
        "subgroup_index": 10,
        "raw_data_snapshot": {"values": [0.1, 0.2, 0.3]},
        "chart_snapshot_url": "/snapshots/chart_001.png",
        "detected_by": "auto"
    }


@pytest.fixture
def sample_ocap_step():
    return {
        "phase": "containment",
        "step_number": 1,
        "action_type": "immediate",
        "action_description": "立即停止生产线",
        "responsible_role": "生产主管",
        "responsible_person": "王五",
        "expected_duration_minutes": 15,
        "is_mandatory": True,
        "prerequisites": [],
        "sort_order": 1
    }


@pytest.fixture
def sample_ocap_execution():
    return {
        "status": "in_progress",
        "started_at": "2026-03-07T10:30:00",
        "executed_by": "测试执行人",
        "notes": "正在执行遏制措施",
        "evidence_urls": ["/evidence/doc1.pdf", "/evidence/image1.png"],
        "containment_action_taken": "已隔离批次产品"
    }


@pytest.fixture
def sample_ocap_root_cause():
    return {
        "analysis_method": "5whys",
        "why_1": "为什么出现缺陷？因为设备参数偏移",
        "why_2": "为什么设备参数偏移？因为维护不及时",
        "why_3": "为什么维护不及时？因为维护计划未执行",
        "why_4": "为什么维护计划未执行？因为人员不足",
        "why_5": "为什么人员不足？因为预算削减",
        "root_cause_description": "根本原因：预算削减导致维护人员不足，进而导致设备维护不及时",
        "contributing_factors": ["人员培训不足", "备件库存低"],
        "verified": False
    }


@pytest.fixture
def sample_ocap_corrective_action():
    return {
        "action_description": "增加维护人员编制",
        "action_type": "permanent",
        "responsible_person": "生产经理",
        "target_date": "2026-04-01",
        "status": "planned"
    }
