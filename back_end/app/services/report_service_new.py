"""
报告导出服务模块 - 优化版

使用 Jinja2 模板引擎，基于创建好的 HTML 模板文件
提供控制计划、SPC 能力分析和 OCAP 的报告导出功能
"""

import os
from io import BytesIO
from typing import List, Any, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from fastapi import Response, HTTPException
from jinja2 import Environment, FileSystemLoader

from app.models.models import ControlPlan, ControlPlanItem, OCAP, OCAPSignal, OCAPStep, OCAPExecution, OCAPRootCause, OCAPCorrectiveAction

# 模板引擎配置
template_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'templates', 'reports')
jinja_env = Environment(loader=FileSystemLoader(template_dir))


def export_control_plan_html(plan_id: int, db: Session) -> Response:
    """
    按照 AIAG/VDA 标准格式导出控制计划 HTML
    使用创建好的 control_plan_report.html 模板
    """
    plan = db.query(ControlPlan).filter(ControlPlan.id == plan_id).first()
    if not plan:
        raise HTTPException(status_code=404, detail=f"控制计划 {plan_id} 不存在")
    
    items = db.query(ControlPlanItem).filter(
        ControlPlanItem.control_plan_id == plan_id
    ).order_by(ControlPlanItem.sort_order).all()
    
    # 加载模板
    template = jinja_env.get_template('control_plan_report.html')
    
    # 准备模板数据
    template_data = {
        'plan_type': plan.plan_type or 'production',
        'page_number': plan.page_number or 1,
        'total_pages': plan.total_pages or 1,
        'control_plan_number': plan.control_plan_number or '',
        'part_number': plan.part_number or '',
        'latest_change_level': plan.latest_change_level or '',
        'part_name': plan.part_name or '',
        'organization_plant': plan.organization_plant or '',
        'organization_code': plan.organization_code or '',
        'key_contact': plan.key_contact or '',
        'core_team': plan.core_team or '',
        'date_orig': plan.date_orig.strftime('%Y-%m-%d') if plan.date_orig else '',
        'date_rev': plan.date_rev.strftime('%Y-%m-%d') if plan.date_rev else '',
        'org_approval': plan.org_approval_by or '',
        'customer_eng_approval': plan.customer_eng_approval_by or '',
        'customer_quality_approval': plan.customer_quality_approval_by or '',
        'other_approval': plan.other_approval_by or '',
        'items': items,
        'generated_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'plan_id': plan_id
    }
    
    # 渲染模板
    html_content = template.render(**template_data)
    
    # 生成文件名
    filename = f"ControlPlan_{plan.part_number or plan.id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
    
    return Response(
        content=html_content,
        media_type="text/html",
        headers={"Content-Disposition": f"attachment; filename*=UTF-8''{filename}"}
    )


def export_capability_analysis_html(analysis_id: int, db: Session) -> Response:
    """
    按照 AIAG/VDA SPC 标准格式导出过程能力分析报告 HTML
    使用创建好的 spc_capability_report.html 模板
    """
    from app.models.models import CapabilityAnalysis
    
    analysis = db.query(CapabilityAnalysis).filter(CapabilityAnalysis.id == analysis_id).first()
    if not analysis:
        raise HTTPException(status_code=404, detail=f"能力分析 {analysis_id} 不存在")
    
    # 加载模板
    template = jinja_env.get_template('spc_capability_report.html')
    
    # 准备数据
    data_values = analysis.data_values if hasattr(analysis, 'data_values') and analysis.data_values else []
    
    template_data = {
        'process_name': analysis.analysis_name or '',
        'machine_name': '',
        'study_location': '',
        'process_id': '',
        'machine_id': '',
        'operator_name': '',
        'study_date': analysis.analysis_time.strftime('%Y-%m-%d') if analysis.analysis_time else '',
        'start_time': '',
        'end_time': '',
        'part_name_id': f"{analysis.part_name or ''}, ID: {analysis.part_id or ''}" if hasattr(analysis, 'part_name') else '',
        'characteristic_name_id': f"{analysis.characteristic_name or ''}, ID: {analysis.characteristic_id or ''}" if hasattr(analysis, 'characteristic_name') else '',
        'lsl': f"{float(analysis.lsl):.4f}" if analysis.lsl else '',
        'usl': f"{float(analysis.usl):.4f}" if analysis.usl else '',
        'study_remarks': '',
        'sample_size': analysis.sample_count or '',
        'subgroup_size': analysis.subgroup_count or '',
        'sampling_strategy': '',
        'x50': f"{float(analysis.mean):.4f}" if analysis.mean else '',
        'variation_estimate': f"{6 * float(analysis.sigma_within):.4f}" if analysis.sigma_within else '',
        'distribution_model': 'Normal Distribution',
        'cp_g': '1.67',
        'cpk_g': '1.33',
        'calculation_method': 'Geometric Method',
        'cp': f"{float(analysis.cp):.3f}" if analysis.cp else '',
        'cpk': f"{float(analysis.cpk):.3f}" if analysis.cpk else '',
        'cp_ci_lower': '',
        'cp_ci_upper': '',
        'cpk_ci_lower': '',
        'cpk_ci_upper': '',
        'p_usl': '0.00000%',
        'ppm_usl': '0.0',
        'p_lsl': '0.00000%',
        'ppm_lsl': '0.0',
        'conclusion': get_capability_conclusion(float(analysis.cpk) if analysis.cpk else 0),
        'generated_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'analysis_id': analysis_id
    }
    
    # 渲染模板
    html_content = template.render(**template_data)
    
    # 生成文件名
    filename = f"SPC_Capability_{analysis.analysis_name or analysis_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
    
    return Response(
        content=html_content,
        media_type="text/html",
        headers={"Content-Disposition": f"attachment; filename*=UTF-8''{filename}"}
    )


def export_ocap_html(ocap_id: int, db: Session) -> Response:
    """
    导出 OCAP 响应计划 HTML 报告
    使用创建好的 ocap_response_report.html 模板
    """
    ocap = db.query(OCAP).filter(OCAP.id == ocap_id).first()
    if not ocap:
        raise HTTPException(status_code=404, detail=f"OCAP {ocap_id} 不存在")
    
    signals = db.query(OCAPSignal).filter(OCAPSignal.ocap_id == ocap_id).all()
    steps = db.query(OCAPStep).filter(OCAPStep.ocap_id == ocap_id).order_by(OCAPStep.phase, OCAPStep.sort_order).all()
    root_causes = db.query(OCAPRootCause).filter(OCAPRootCause.ocap_id == ocap_id).all()
    actions = db.query(OCAPCorrectiveAction).filter(OCAPCorrectiveAction.ocap_id == ocap_id).all()
    
    # 加载模板
    template = jinja_env.get_template('ocap_response_report.html')
    
    # 优先级映射
    priority_class_map = {
        'critical': 'critical',
        'high': 'high',
        'medium': 'medium',
        'low': 'low'
    }
    
    priority_text_map = {
        'critical': 'CRITICAL PRIORITY',
        'high': 'HIGH PRIORITY',
        'medium': 'MEDIUM PRIORITY',
        'low': 'LOW PRIORITY'
    }
    
    # 准备模板数据
    template_data = {
        'ocap_number': ocap.ocap_number or '',
        'title': ocap.title or '',
        'priority_class': priority_class_map.get(ocap.priority or 'medium', 'medium'),
        'priority_text': priority_text_map.get(ocap.priority or 'medium', 'MEDIUM PRIORITY'),
        'production_line': ocap.line.line_name if ocap.line else '',
        'assigned_to': ocap.assigned_to or '',
        'status': ocap.status or '',
        'created_time': ocap.created_at.strftime('%Y-%m-%d %H:%M') if ocap.created_at else '',
        'total_signals': len(signals),
        'total_steps': len(steps),
        'total_root_causes': len(root_causes),
        'total_actions': len(actions),
        'signals': [{
            'signal_type': signal.signal_type or '',
            'rule': signal.rule or '',
            'measurement_value': str(signal.measurement_value) if signal.measurement_value else '',
            'triggered_time': signal.triggered_at.strftime('%Y-%m-%d %H:%M') if signal.triggered_at else '',
            'status': signal.status or ''
        } for signal in signals],
        'steps': [{
            'phase': step.phase or '',
            'phase_class': get_phase_class(step.phase),
            'description': step.description or '',
            'responsible': step.responsible or '',
            'status': step.status or '',
            'completion_time': step.completed_at.strftime('%Y-%m-%d %H:%M') if step.completed_at else ''
        } for step in steps],
        'root_causes': [{
            'description': cause.description or '',
            'category': cause.category or ''
        } for cause in root_causes],
        'actions': [{
            'title': action.title or '',
            'description': action.description or '',
            'owner': action.owner or '',
            'due_date': action.due_date.strftime('%Y-%m-%d') if action.due_date else '',
            'status': action.status or '',
            'status_class': get_action_status_class(action.status)
        } for action in actions],
        'generated_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'ocap_id': ocap_id
    }
    
    # 渲染模板
    html_content = template.render(**template_data)
    
    # 生成文件名
    filename = f"OCAP_{ocap.ocap_number or ocap.id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
    
    return Response(
        content=html_content,
        media_type="text/html",
        headers={"Content-Disposition": f"attachment; filename*=UTF-8''{filename}"}
    )


def get_phase_class(phase: str) -> str:
    """获取阶段对应的 CSS 类名"""
    phase_map = {
        'detection': 'detection',
        'containment': 'containment',
        'corrective': 'corrective',
        'verification': 'verification'
    }
    return phase_map.get(phase.lower() if phase else '', 'detection')


def get_action_status_class(status: str) -> str:
    """获取措施状态对应的 CSS 类名"""
    status_map = {
        'completed': 'completed',
        'in_progress': 'in-progress',
        'pending': 'pending'
    }
    return status_map.get(status.lower() if status else '', 'pending')


def get_capability_conclusion(cpk: float) -> str:
    """根据 Cpk 值生成结论"""
    if cpk >= 1.67:
        return 'The Cpk, Cpk,G requirements are met, process is demonstrated to be stable over time, process capability is excellent, no actions required, continue to monitor per plan.'
    elif cpk >= 1.33:
        return 'The Cpk, Cpk,G requirements are met, process is demonstrated to be stable over time, process capability is good, continue to monitor per plan.'
    elif cpk >= 1.0:
        return 'Process capability is fair, process is marginally capable. Recommend analyzing sources of variation and developing improvement plans.'
    else:
        return 'Process capability is poor, process is not capable. Immediate corrective actions and comprehensive process improvement are required.'
