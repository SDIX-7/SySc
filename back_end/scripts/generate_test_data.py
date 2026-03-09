"""
测试数据生成脚本
生成产线、控制计划、OCAP等测试数据
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime, timedelta
import random
from sqlalchemy.orm import Session
from app.database import SessionLocal, engine, Base
from app.models.models import (
    ProductionLine, ControlChartConfig, AttributeData, MeasurementData,
    ControlPlan, ControlPlanItem, OCAP, OCAPSignal, OCAPStep, 
    OCAPExecution, OCAPRootCause, OCAPCorrectiveAction
)

Base.metadata.create_all(bind=engine)

def random_date(start_days_ago=30):
    return datetime.now() - timedelta(days=random.randint(0, start_days_ago), hours=random.randint(0, 23))

def create_production_lines(db: Session):
    lines_data = [
        {
            "line_code": "LINE-001",
            "line_name": "发动机缸体加工线",
            "line_description": "发动机缸体精加工生产线，负责缸体的镗孔、磨削等工序",
            "data_type": "measurement",
            "status": "active"
        },
        {
            "line_code": "LINE-002", 
            "line_name": "变速箱装配线",
            "line_description": "变速箱总成装配线，负责齿轮组装和壳体装配",
            "data_type": "attribute",
            "status": "active"
        },
        {
            "line_code": "LINE-003",
            "line_name": "曲轴加工线",
            "line_description": "曲轴精加工生产线，负责曲轴的车削、磨削工序",
            "data_type": "measurement",
            "status": "active"
        },
        {
            "line_code": "LINE-004",
            "line_name": "连杆加工线",
            "line_description": "连杆生产线，负责连杆的锻造和机加工",
            "data_type": "measurement",
            "status": "active"
        },
        {
            "line_code": "LINE-005",
            "line_name": "缸盖装配线",
            "line_description": "发动机缸盖装配线，负责气门机构和凸轮轴装配",
            "data_type": "attribute",
            "status": "active"
        }
    ]
    
    lines = []
    for data in lines_data:
        existing = db.query(ProductionLine).filter(ProductionLine.line_code == data["line_code"]).first()
        if existing:
            lines.append(existing)
            continue
        line = ProductionLine(**data)
        db.add(line)
        db.commit()
        db.refresh(line)
        lines.append(line)
        print(f"创建产线: {line.line_name} (ID: {line.id})")
    
    return lines

def create_control_chart_configs(db: Session, lines):
    configs = []
    for line in lines:
        existing = db.query(ControlChartConfig).filter(ControlChartConfig.line_id == line.id).first()
        if existing:
            configs.append(existing)
            continue
        
        chart_type = "Xbar-R" if line.data_type == "measurement" else "U"
        config = ControlChartConfig(
            line_id=line.id,
            chart_type=chart_type,
            control_limit_type="dynamic",
            alarm_rules='["rule_1_beyond_limits", "rule_2_9_in_a_row", "rule_3_6_trending"]'
        )
        db.add(config)
        db.commit()
        db.refresh(config)
        configs.append(config)
        print(f"创建控制图配置: {line.line_name} - {chart_type}")
    
    return configs

def create_attribute_data(db: Session, line):
    for i in range(25):
        sample_id = f"{line.line_code}-S{str(i+1).zfill(3)}"
        existing = db.query(AttributeData).filter(
            AttributeData.line_id == line.id,
            AttributeData.sample_id == sample_id
        ).first()
        if existing:
            continue
        
        sample_size = random.randint(80, 120)
        defect_count = random.choice([0, 0, 0, 1, 1, 2, 3]) if random.random() > 0.1 else random.randint(3, 8)
        
        data = AttributeData(
            line_id=line.id,
            sample_id=sample_id,
            sample_size=sample_size,
            defect_count=defect_count,
            inspector=f"检验员{random.choice(['张三', '李四', '王五', '赵六'])}",
            inspection_time=random_date(60)
        )
        db.add(data)
    
    db.commit()
    print(f"为 {line.line_name} 创建属性数据")

def create_measurement_data(db: Session, line):
    for i in range(25):
        sample_id = f"{line.line_code}-M{str(i+1).zfill(3)}"
        existing = db.query(MeasurementData).filter(
            MeasurementData.line_id == line.id,
            MeasurementData.sample_id == sample_id
        ).first()
        if existing:
            continue
        
        subgroup_size = 5
        base_value = random.uniform(50.0, 100.0)
        values = [round(base_value + random.uniform(-2, 2), 3) for _ in range(subgroup_size)]
        
        data = MeasurementData(
            line_id=line.id,
            sample_id=sample_id,
            measurement_values=str(values),
            operator=f"操作员{random.choice(['张三', '李四', '王五', '赵六'])}",
            equipment=f"测量仪{random.choice(['A', 'B', 'C'])}",
            measurement_time=random_date(60)
        )
        db.add(data)
    
    db.commit()
    print(f"为 {line.line_name} 创建计量数据")

def create_control_plans(db: Session, lines):
    control_plans = []
    
    plan_templates = [
        {
            "line_idx": 0,
            "part_number": "ENG-BLOCK-001",
            "part_name": "发动机缸体",
            "plan_type": "production",
            "items": [
                {
                    "process_name": "缸孔镗削",
                    "operation_description": "精镗缸孔至最终尺寸",
                    "characteristic_no": "CP-001",
                    "product_characteristic": "缸孔直径",
                    "specification_tolerance": "Φ85.00±0.02mm",
                    "evaluation_measurement_technique": "内径千分尺",
                    "sample_size": "5件",
                    "sample_frequency": "每2小时",
                    "control_method": "Xbar-R控制图",
                    "reaction_plan": "停止生产，通知工艺工程师"
                },
                {
                    "process_name": "缸孔珩磨",
                    "operation_description": "珩磨缸孔表面",
                    "characteristic_no": "CP-002",
                    "product_characteristic": "缸孔表面粗糙度",
                    "specification_tolerance": "Ra0.4-0.8μm",
                    "evaluation_measurement_technique": "粗糙度仪",
                    "sample_size": "3件",
                    "sample_frequency": "每4小时",
                    "control_method": "Xbar-R控制图",
                    "reaction_plan": "调整珩磨参数"
                },
                {
                    "process_name": "主轴承孔加工",
                    "operation_description": "精镗主轴承孔",
                    "characteristic_no": "CP-003",
                    "product_characteristic": "主轴承孔同轴度",
                    "specification_tolerance": "≤0.03mm",
                    "evaluation_measurement_technique": "三坐标测量机",
                    "sample_size": "1件",
                    "sample_frequency": "每班",
                    "control_method": "单值控制图",
                    "reaction_plan": "检查夹具定位"
                }
            ]
        },
        {
            "line_idx": 1,
            "part_number": "TRANS-ASSY-001",
            "part_name": "变速箱总成",
            "plan_type": "production",
            "items": [
                {
                    "process_name": "齿轮装配",
                    "operation_description": "齿轮组件装配",
                    "characteristic_no": "GA-001",
                    "product_characteristic": "齿轮啮合间隙",
                    "specification_tolerance": "0.15-0.25mm",
                    "evaluation_measurement_technique": "塞尺测量",
                    "sample_size": "5台",
                    "sample_frequency": "每小时",
                    "control_method": "U控制图",
                    "reaction_plan": "调整齿轮选配"
                },
                {
                    "process_name": "壳体密封",
                    "operation_description": "壳体结合面密封",
                    "characteristic_no": "GA-002",
                    "product_characteristic": "密封胶涂布量",
                    "specification_tolerance": "规定量±10%",
                    "evaluation_measurement_technique": "重量法",
                    "sample_size": "3台",
                    "sample_frequency": "每2小时",
                    "control_method": "U控制图",
                    "reaction_plan": "调整涂胶参数"
                }
            ]
        },
        {
            "line_idx": 2,
            "part_number": "CRANK-001",
            "part_name": "曲轴",
            "plan_type": "production",
            "items": [
                {
                    "process_name": "主轴颈磨削",
                    "operation_description": "精磨主轴颈",
                    "characteristic_no": "CN-001",
                    "product_characteristic": "主轴颈直径",
                    "specification_tolerance": "Φ60.00±0.01mm",
                    "evaluation_measurement_technique": "外径千分尺",
                    "sample_size": "5件",
                    "sample_frequency": "每2小时",
                    "control_method": "Xbar-R控制图",
                    "reaction_plan": "修整砂轮"
                },
                {
                    "process_name": "曲柄销磨削",
                    "operation_description": "精磨曲柄销",
                    "characteristic_no": "CN-002",
                    "product_characteristic": "曲柄销直径",
                    "specification_tolerance": "Φ50.00±0.01mm",
                    "evaluation_measurement_technique": "外径千分尺",
                    "sample_size": "5件",
                    "sample_frequency": "每2小时",
                    "control_method": "Xbar-R控制图",
                    "reaction_plan": "修整砂轮"
                },
                {
                    "process_name": "动平衡",
                    "operation_description": "曲轴动平衡校正",
                    "characteristic_no": "CN-003",
                    "product_characteristic": "不平衡量",
                    "specification_tolerance": "≤5g·cm",
                    "evaluation_measurement_technique": "动平衡机",
                    "sample_size": "全检",
                    "sample_frequency": "100%",
                    "control_method": "P控制图",
                    "reaction_plan": "重新校正平衡"
                }
            ]
        }
    ]
    
    for template in plan_templates:
        line = lines[template["line_idx"]]
        
        existing = db.query(ControlPlan).filter(
            ControlPlan.line_id == line.id,
            ControlPlan.part_number == template["part_number"]
        ).first()
        
        if existing:
            control_plans.append(existing)
            continue
        
        plan = ControlPlan(
            line_id=line.id,
            plan_type=template["plan_type"],
            control_plan_number=f"CP-{line.line_code}-{datetime.now().strftime('%Y%m%d')}",
            part_number=template["part_number"],
            part_name=template["part_name"],
            part_description=f"{template['part_name']}生产控制计划",
            organization_plant="第一制造工厂",
            organization_code="PLANT-001",
            key_contact="张工程师",
            key_contact_phone="13800138000",
            core_team="工艺部,质量部,生产部",
            org_approval_date=datetime.now() - timedelta(days=10),
            org_approval_by="李经理",
            version="1.0",
            status="active",
            created_by="系统管理员"
        )
        db.add(plan)
        db.commit()
        db.refresh(plan)
        
        for idx, item_data in enumerate(template["items"]):
            item = ControlPlanItem(
                control_plan_id=plan.id,
                part_process_number=f"P{str(idx+1).zfill(2)}",
                process_name=item_data["process_name"],
                operation_description=item_data["operation_description"],
                characteristic_no=item_data["characteristic_no"],
                product_characteristic=item_data["product_characteristic"],
                specification_tolerance=item_data["specification_tolerance"],
                evaluation_measurement_technique=item_data["evaluation_measurement_technique"],
                sample_size=item_data["sample_size"],
                sample_frequency=item_data["sample_frequency"],
                control_method=item_data["control_method"],
                reaction_plan=item_data["reaction_plan"],
                sort_order=idx + 1
            )
            db.add(item)
        
        db.commit()
        control_plans.append(plan)
        print(f"创建控制计划: {plan.part_name} - {plan.control_plan_number}")
    
    return control_plans

def create_ocaps(db: Session, lines, configs):
    ocaps = []
    
    ocap_templates = [
        {
            "line_idx": 0,
            "name": "缸孔直径超出控制限OCAP",
            "description": "当缸孔直径测量值超出控制限时启动此OCAP",
            "signal_type": "point_beyond_limits",
            "priority": "high",
            "severity_score": 8,
            "scope_score": 6,
            "trend_score": 5,
            "steps": [
                {"phase": "containment", "action_description": "立即停止该工序生产", "responsible_role": "操作员", "expected_duration_minutes": 5},
                {"phase": "containment", "action_description": "隔离可疑产品，标识并记录", "responsible_role": "检验员", "expected_duration_minutes": 15},
                {"phase": "investigation", "action_description": "检查刀具磨损情况", "responsible_role": "工艺工程师", "expected_duration_minutes": 30},
                {"phase": "investigation", "action_description": "检查机床主轴精度", "responsible_role": "设备工程师", "expected_duration_minutes": 45},
                {"phase": "correction", "action_description": "更换磨损刀具或调整参数", "responsible_role": "工艺工程师", "expected_duration_minutes": 60},
                {"phase": "verification", "action_description": "重新取样验证过程能力", "responsible_role": "质量工程师", "expected_duration_minutes": 120}
            ],
            "root_cause": {
                "why_1": "缸孔直径超出公差",
                "why_2": "镗刀磨损导致切削量变化",
                "why_3": "刀具寿命管理不当",
                "why_4": "预防性维护计划不完善",
                "why_5": "缺乏刀具磨损监控系统"
            },
            "corrective_action": "安装刀具磨损在线监测系统"
        },
        {
            "line_idx": 1,
            "name": "齿轮装配缺陷率上升OCAP",
            "description": "当齿轮装配缺陷率连续上升时启动此OCAP",
            "signal_type": "trend",
            "priority": "medium",
            "severity_score": 5,
            "scope_score": 7,
            "trend_score": 6,
            "steps": [
                {"phase": "containment", "action_description": "增加检验频次至100%全检", "responsible_role": "检验员", "expected_duration_minutes": 10},
                {"phase": "containment", "action_description": "追溯最近批次产品", "responsible_role": "质量工程师", "expected_duration_minutes": 30},
                {"phase": "investigation", "action_description": "检查齿轮来料质量", "responsible_role": "来料检验员", "expected_duration_minutes": 45},
                {"phase": "investigation", "action_description": "检查装配工装状态", "responsible_role": "工艺工程师", "expected_duration_minutes": 30},
                {"phase": "correction", "action_description": "更换不良齿轮批次或修复工装", "responsible_role": "生产主管", "expected_duration_minutes": 90},
                {"phase": "verification", "action_description": "连续监控3个批次确认改善", "responsible_role": "质量工程师", "expected_duration_minutes": 240}
            ],
            "root_cause": {
                "why_1": "齿轮装配缺陷率上升",
                "why_2": "齿轮啮合间隙超差",
                "why_3": "齿轮供应商批次质量问题",
                "why_4": "供应商过程能力下降",
                "why_5": "供应商未按控制计划执行"
            },
            "corrective_action": "加强供应商质量审核，增加进货检验频次"
        },
        {
            "line_idx": 2,
            "name": "曲轴不平衡量超标OCAP",
            "description": "当曲轴动平衡检测发现不平衡量超标时启动",
            "signal_type": "point_beyond_limits",
            "priority": "critical",
            "severity_score": 9,
            "scope_score": 8,
            "trend_score": 4,
            "steps": [
                {"phase": "containment", "action_description": "立即停止动平衡工序", "responsible_role": "操作员", "expected_duration_minutes": 5},
                {"phase": "containment", "action_description": "隔离所有未通过动平衡的曲轴", "responsible_role": "检验员", "expected_duration_minutes": 20},
                {"phase": "investigation", "action_description": "检查动平衡机校准状态", "responsible_role": "设备工程师", "expected_duration_minutes": 30},
                {"phase": "investigation", "action_description": "分析曲轴加工过程数据", "responsible_role": "工艺工程师", "expected_duration_minutes": 60},
                {"phase": "correction", "action_description": "重新校准动平衡机或调整加工参数", "responsible_role": "设备工程师", "expected_duration_minutes": 120},
                {"phase": "verification", "action_description": "使用标准件验证设备精度", "responsible_role": "质量工程师", "expected_duration_minutes": 60}
            ],
            "root_cause": {
                "why_1": "曲轴不平衡量超标",
                "why_2": "材料密度不均匀",
                "why_3": "锻造工艺参数波动",
                "why_4": "原材料批次差异",
                "why_5": "供应商材料检验不严格"
            },
            "corrective_action": "加强原材料入厂检验，增加材料密度抽检"
        }
    ]
    
    for template in ocap_templates:
        line = lines[template["line_idx"]]
        config = configs[template["line_idx"]]
        
        existing = db.query(OCAP).filter(
            OCAP.line_id == line.id,
            OCAP.name == template["name"]
        ).first()
        
        if existing:
            ocaps.append(existing)
            continue
        
        overall_score = int((template["severity_score"] + template["scope_score"] + template["trend_score"]) / 3)
        
        ocap = OCAP(
            control_chart_config_id=config.id,
            line_id=line.id,
            name=template["name"],
            description=template["description"],
            signal_type=template["signal_type"],
            priority=template["priority"],
            severity_score=template["severity_score"],
            scope_score=template["scope_score"],
            trend_score=template["trend_score"],
            overall_priority_score=overall_score,
            status="active",
            is_active=True,
            created_by="系统管理员"
        )
        db.add(ocap)
        db.commit()
        db.refresh(ocap)
        
        for idx, step_data in enumerate(template["steps"]):
            step = OCAPStep(
                ocap_id=ocap.id,
                phase=step_data["phase"],
                step_number=idx + 1,
                action_type="immediate" if step_data["phase"] == "containment" else "short_term",
                action_description=step_data["action_description"],
                responsible_role=step_data["responsible_role"],
                expected_duration_minutes=step_data["expected_duration_minutes"],
                is_mandatory=True,
                sort_order=idx + 1
            )
            db.add(step)
        
        signal = OCAPSignal(
            ocap_id=ocap.id,
            signal_time=datetime.now() - timedelta(days=random.randint(1, 7)),
            signal_type=template["signal_type"],
            signal_value="超出控制限" if template["signal_type"] == "point_beyond_limits" else "连续上升",
            control_limit_value="UCL=3σ",
            detected_by="auto"
        )
        db.add(signal)
        
        root_cause_data = template["root_cause"]
        root_cause = OCAPRootCause(
            ocap_id=ocap.id,
            analysis_method="5whys",
            why_1=root_cause_data["why_1"],
            why_2=root_cause_data["why_2"],
            why_3=root_cause_data["why_3"],
            why_4=root_cause_data["why_4"],
            why_5=root_cause_data["why_5"],
            root_cause_description=root_cause_data["why_5"],
            verified=True,
            verified_by="质量工程师",
            verified_at=datetime.now() - timedelta(days=random.randint(1, 5))
        )
        db.add(root_cause)
        db.commit()
        db.refresh(root_cause)
        
        corrective = OCAPCorrectiveAction(
            ocap_id=ocap.id,
            root_cause_id=root_cause.id,
            action_description=template["corrective_action"],
            action_type="permanent",
            responsible_person="工艺工程师",
            target_date=datetime.now() + timedelta(days=30),
            status="planned"
        )
        db.add(corrective)
        
        db.commit()
        ocaps.append(ocap)
        print(f"创建OCAP: {ocap.name} (优先级: {ocap.priority})")
    
    return ocaps

def main():
    db = SessionLocal()
    try:
        print("=" * 60)
        print("开始生成测试数据...")
        print("=" * 60)
        
        print("\n1. 创建产线数据...")
        lines = create_production_lines(db)
        
        print("\n2. 创建控制图配置...")
        configs = create_control_chart_configs(db, lines)
        
        print("\n3. 创建检测数据...")
        for line in lines:
            if line.data_type == "attribute":
                create_attribute_data(db, line)
            else:
                create_measurement_data(db, line)
        
        print("\n4. 创建控制计划...")
        control_plans = create_control_plans(db, lines)
        
        print("\n5. 创建OCAP...")
        ocaps = create_ocaps(db, lines, configs)
        
        print("\n" + "=" * 60)
        print("测试数据生成完成!")
        print("=" * 60)
        print(f"\n统计:")
        print(f"  - 产线: {len(lines)} 条")
        print(f"  - 控制图配置: {len(configs)} 个")
        print(f"  - 控制计划: {len(control_plans)} 个")
        print(f"  - OCAP: {len(ocaps)} 个")
        
    except Exception as e:
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    main()
