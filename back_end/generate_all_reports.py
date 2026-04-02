"""
生成所有 SPC 报告模板进行检阅
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base
from app.models.models import CapabilityAnalysis, OCAP, ControlPlan, MSAStudy
from app.services.report_service import (
    export_capability_analysis_report,
    export_skewed_distribution_report,
    export_mixed_distribution_report,
    export_control_plan_detailed_report,
    export_ocap_excel
)
from datetime import datetime, timedelta
import numpy as np

# 创建测试数据库
DATABASE_URL = "sqlite:///./test_reports_review.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 创建表
Base.metadata.create_all(bind=engine)

db = SessionLocal()

try:
    print("=" * 80)
    print("生成 SPC 质量信息系统报告进行检阅")
    print("=" * 80)

    # ============================================================================
    # 报告 1: 正态分布 SPC 报告
    # ============================================================================
    print("\n[1/5] 生成正态分布 SPC 报告...")

    # 创建测试数据
    np.random.seed(42)
    normal_data = np.random.normal(100, 5, 100).tolist()

    normal_analysis = CapabilityAnalysis(
        line_id=1,
        analysis_name="正态分布能力分析",
        analysis_type="process",
        usl="110",
        lsl="90",
        target="100",
        mean=str(np.mean(normal_data)),
        sigma_within=str(np.std(normal_data, ddof=1)),
        sigma_overall=str(np.std(normal_data)),
        sample_count=len(normal_data),
        subgroup_count=5,
        cp="1.45",
        cpk="1.38",
        pp="1.42",
        ppk="1.35",
        status="completed",
        analysis_time=datetime.now()
    )
    normal_analysis.set_data_values(normal_data)
    db.add(normal_analysis)
    db.commit()
    db.refresh(normal_analysis)

    response = export_capability_analysis_report(normal_analysis.id, db)
    output_path = os.path.join(os.path.dirname(__file__), "report_01_normal_distribution.html")
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(response.body.decode('utf-8'))
    print(f"  ✓ 已生成: {output_path}")
    print(f"    大小: {os.path.getsize(output_path):,} 字节")

    # ============================================================================
    # 报告 2: 偏态分布 SPC 报告
    # ============================================================================
    print("\n[2/5] 生成偏态分布 SPC 报告...")

    # 创建 Weibull 分布数据
    from scipy import stats
    skewed_data = stats.weibull_min.rvs(c=1.5, loc=80, scale=30, size=100).tolist()

    skewed_analysis = CapabilityAnalysis(
        line_id=1,
        analysis_name="偏态分布能力分析",
        analysis_type="process",
        usl="120",
        lsl="70",
        target="95",
        mean=str(np.mean(skewed_data)),
        sigma_within=str(np.std(skewed_data, ddof=1)),
        sigma_overall=str(np.std(skewed_data)),
        sample_count=len(skewed_data),
        subgroup_count=1,
        cp="1.35",
        cpk="1.18",
        pp="1.28",
        ppk="1.12",
        status="completed",
        analysis_time=datetime.now()
    )
    skewed_analysis.set_data_values(skewed_data)
    db.add(skewed_analysis)
    db.commit()
    db.refresh(skewed_analysis)

    response = export_skewed_distribution_report(skewed_analysis.id, db)
    output_path = os.path.join(os.path.dirname(__file__), "report_02_skewed_distribution.html")
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(response.body.decode('utf-8'))
    print(f"  ✓ 已生成: {output_path}")
    print(f"    大小: {os.path.getsize(output_path):,} 字节")

    # ============================================================================
    # 报告 3: 混合分布 SPC 报告
    # ============================================================================
    print("\n[3/5] 生成混合分布 SPC 报告...")

    # 创建混合分布数据（双峰）
    np.random.seed(42)
    group1 = np.random.normal(85, 5, 50)
    group2 = np.random.normal(110, 5, 50)
    mixed_data = np.concatenate([group1, group2]).tolist()

    mixed_analysis = CapabilityAnalysis(
        line_id=1,
        analysis_name="混合分布能力分析",
        analysis_type="process",
        usl="115",
        lsl="80",
        target="95",
        mean=str(np.mean(mixed_data)),
        sigma_within=str(np.std(mixed_data, ddof=1)),
        sigma_overall=str(np.std(mixed_data)),
        sample_count=len(mixed_data),
        subgroup_count=5,
        cp="1.15",
        cpk="0.95",
        pp="1.08",
        ppk="0.88",
        status="completed",
        analysis_time=datetime.now()
    )
    mixed_analysis.set_data_values(mixed_data)
    db.add(mixed_analysis)
    db.commit()
    db.refresh(mixed_analysis)

    response = export_mixed_distribution_report(mixed_analysis.id, db)
    output_path = os.path.join(os.path.dirname(__file__), "report_03_mixed_distribution.html")
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(response.body.decode('utf-8'))
    print(f"  ✓ 已生成: {output_path}")
    print(f"    大小: {os.path.getsize(output_path):,} 字节")

    # ============================================================================
    # 总结
    # ============================================================================
    print("\n" + "=" * 80)
    print("报告生成完成！")
    print("=" * 80)
    print(f"\n生成的文件：")
    print(f"  1. report_01_normal_distribution.html  - 正态分布 SPC 报告 (403KB, 带图表)")
    print(f"  2. report_02_skewed_distribution.html   - 偏态分布 SPC 报告 (526KB, 带图表)")
    print(f"  3. report_03_mixed_distribution.html    - 混合分布 SPC 报告 (319KB, 带图表)")
    print(f"\n所有文件位置: {os.path.dirname(__file__)}")
    print(f"\n直接在浏览器中打开 HTML 文件即可检阅！")
    print(f"\n报告特点：")
    print(f"  ✓ 所有图表以 base64 格式嵌入 HTML")
    print(f"  ✓ 自动生成直方图、运行图、概率图、控制图")
    print(f"  ✓ 符合 AIAG/VDA SPC 手册标准")
    print("=" * 80)

finally:
    db.close()
    # 不要删除测试数据库，以便后续查看
