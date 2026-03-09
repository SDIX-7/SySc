"""
报告导出服务模块

提供控制计划和OCAP的报告导出功能
"""

import io
from io import BytesIO
from typing import Dict, List, Any, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from fastapi import Response, HTTPException

from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, Border, PatternFill, Side
from openpyxl.utils import get_column_letter

from app.models.models import ControlPlan, ControlPlanItem, OCAP, OCAPSignal, OCAPStep, OCAPExecution, OCAPRootCause, OCAPCorrectiveAction


thin_border = Border(
    left=Side(style='thin'),
    right=Side(style='thin'),
    top=Side(style='thin'),
    bottom=Side(style='thin')
)


def export_control_plan_excel(plan_id: int, db: Session) -> Response:
    plan = db.query(ControlPlan).filter(ControlPlan.id == plan_id).first()
    if not plan:
        raise HTTPException(status_code=404, detail=f"控制计划 {plan_id} 不存在")
    
    items = db.query(ControlPlanItem).filter(
        ControlPlanItem.control_plan_id == plan_id
    ).order_by(ControlPlanItem.sort_order).all()
    
    wb = Workbook()
    ws = wb.active
    ws.title = "控制计划"
    
    header_font = Font(name='微软雅黑', bold=True, size=12)
    header_fill = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")
    header_font_white = Font(name='微软雅黑', bold=True, size=11, color="FFFFFF")
    header_alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)
    cell_alignment = Alignment(horizontal='left', vertical='center', wrap_text=True)
    
    ws.merge_cells('A1:G1')
    ws['A1'] = f"控制计划 - {plan.part_name or plan.control_plan_number or '未命名'}"
    ws['A1'].font = Font(name='微软雅黑', bold=True, size=16)
    ws['A1'].alignment = Alignment(horizontal='center', vertical='center')
    ws.row_dimensions[1].height = 30
    
    info_headers = ['零件号', '零件名称', '零件描述', '变更级别', '组织/工厂', '组织代码', '关键联系人']
    info_values = [
        plan.part_number or '',
        plan.part_name or '',
        plan.part_description or '',
        plan.latest_change_level or '',
        plan.organization_plant or '',
        plan.organization_code or '',
        plan.key_contact or ''
    ]
    
    for col, (header, value) in enumerate(zip(info_headers, info_values), 1):
        cell = ws.cell(row=3, column=col)
        cell.value = f"{header}: {value}"
        cell.font = Font(name='微软雅黑', size=10)
        cell.alignment = cell_alignment
    
    approval_headers = ['组织批准', '其他批准', '客户工程批准', '客户质量批准', '原始日期', '修订日期', '版本']
    approval_values = [
        f"{plan.org_approval_by or ''} {plan.org_approval_date.strftime('%Y-%m-%d') if plan.org_approval_date else ''}",
        f"{plan.other_approval_by or ''} {plan.other_approval_date.strftime('%Y-%m-%d') if plan.other_approval_date else ''}",
        f"{plan.customer_eng_approval_by or ''} {plan.customer_eng_approval_date.strftime('%Y-%m-%d') if plan.customer_eng_approval_date else ''}",
        f"{plan.customer_quality_approval_by or ''} {plan.customer_quality_approval_date.strftime('%Y-%m-%d') if plan.customer_quality_approval_date else ''}",
        plan.date_orig.strftime('%Y-%m-%d') if plan.date_orig else '',
        plan.date_rev.strftime('%Y-%m-%d') if plan.date_rev else '',
        plan.version or '1.0'
    ]
    
    for col, (header, value) in enumerate(zip(approval_headers, approval_values), 1):
        cell = ws.cell(row=4, column=col)
        cell.value = f"{header}: {value}"
        cell.font = Font(name='微软雅黑', size=10)
        cell.alignment = cell_alignment
    
    item_headers = [
        '序号', '零件/过程编号', '过程名称', '作业描述', '机器/装置/夹具/工具',
        '特性编号', '产品特性', '过程特性', '特殊特性等级', '规格/公差',
        '评价/测量技术', '样本容量', '样本频率', '控制方法', '反应计划'
    ]
    
    header_row = 6
    for col, header in enumerate(item_headers, 1):
        cell = ws.cell(row=header_row, column=col)
        cell.value = header
        cell.font = header_font_white
        cell.fill = header_fill
        cell.alignment = header_alignment
        cell.border = thin_border
    
    ws.row_dimensions[header_row].height = 25
    
    col_widths = [6, 15, 15, 20, 20, 10, 20, 20, 12, 15, 20, 10, 12, 20, 20]
    for col, width in enumerate(col_widths, 1):
        ws.column_dimensions[get_column_letter(col)].width = width
    
    for row_idx, item in enumerate(items, header_row + 1):
        row_data = [
            row_idx - header_row,
            item.part_process_number or '',
            item.process_name or '',
            item.operation_description or '',
            item.machine_device_jig_tools or '',
            item.characteristic_no or '',
            item.product_characteristic or '',
            item.process_characteristic or '',
            item.special_characteristic_class or '',
            item.specification_tolerance or '',
            item.evaluation_measurement_technique or '',
            item.sample_size or '',
            item.sample_frequency or '',
            item.control_method or '',
            item.reaction_plan or ''
        ]
        
        for col, value in enumerate(row_data, 1):
            cell = ws.cell(row=row_idx, column=col)
            cell.value = value
            cell.font = Font(name='微软雅黑', size=10)
            cell.alignment = cell_alignment
            cell.border = thin_border
    
    footer_row = header_row + len(items) + 2
    ws.cell(row=footer_row, column=1).value = f"页码: {plan.page_number or 1} / {plan.total_pages or 1}"
    ws.cell(row=footer_row, column=1).font = Font(name='微软雅黑', size=9, italic=True)
    
    ws.cell(row=footer_row, column=5).value = f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    ws.cell(row=footer_row, column=5).font = Font(name='微软雅黑', size=9, italic=True)
    
    output = BytesIO()
    wb.save(output)
    output.seek(0)
    
    filename = f"控制计划_{plan.part_number or plan.id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    
    return Response(
        content=output.getvalue(),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename*=UTF-8''{filename}"}
    )


def export_control_plans_batch_excel(plan_ids: List[int], db: Session) -> Response:
    plans = db.query(ControlPlan).filter(ControlPlan.id.in_(plan_ids)).all()
    if not plans:
        raise HTTPException(status_code=404, detail="未找到指定的控制计划")
    
    wb = Workbook()
    ws = wb.active
    ws.title = "控制计划汇总"
    
    header_font = Font(name='微软雅黑', bold=True, size=11)
    header_fill = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")
    header_font_white = Font(name='微软雅黑', bold=True, size=11, color="FFFFFF")
    header_alignment = Alignment(horizontal='center', vertical='center')
    
    headers = ['ID', '控制计划编号', '零件号', '零件名称', '计划类型', '状态', '版本', '创建时间']
    for col, header in enumerate(headers, 1):
        cell = ws.cell(row=1, column=col)
        cell.value = header
        cell.font = header_font_white
        cell.fill = header_fill
        cell.alignment = header_alignment
        cell.border = thin_border
    
    for row_idx, plan in enumerate(plans, 2):
        row_data = [
            plan.id,
            plan.control_plan_number or '',
            plan.part_number or '',
            plan.part_name or '',
            plan.plan_type or '',
            plan.status or '',
            plan.version or '',
            plan.created_at.strftime('%Y-%m-%d %H:%M') if plan.created_at else ''
        ]
        
        for col, value in enumerate(row_data, 1):
            cell = ws.cell(row=row_idx, column=col)
            cell.value = value
            cell.font = Font(name='微软雅黑', size=10)
            cell.border = thin_border
    
    col_widths = [8, 20, 15, 20, 12, 10, 8, 18]
    for col, width in enumerate(col_widths, 1):
        ws.column_dimensions[get_column_letter(col)].width = width
    
    output = BytesIO()
    wb.save(output)
    output.seek(0)
    
    filename = f"控制计划汇总_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    
    return Response(
        content=output.getvalue(),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename*=UTF-8''{filename}"}
    )


PHASE_LABELS = {
    'containment': '围堵',
    'investigation': '调查',
    'correction': '纠正',
    'verification': '验证'
}

PRIORITY_LABELS = {
    'critical': '紧急',
    'high': '高',
    'medium': '中',
    'low': '低'
}

STATUS_LABELS = {
    'draft': '草稿',
    'active': '激活',
    'executing': '执行中',
    'completed': '已完成',
    'closed': '已关闭'
}


def export_ocap_excel(ocap_id: int, db: Session) -> Response:
    ocap = db.query(OCAP).filter(OCAP.id == ocap_id).first()
    if not ocap:
        raise HTTPException(status_code=404, detail=f"OCAP {ocap_id} 不存在")
    
    signals = db.query(OCAPSignal).filter(OCAPSignal.ocap_id == ocap_id).all()
    steps = db.query(OCAPStep).filter(OCAPStep.ocap_id == ocap_id).order_by(OCAPStep.sort_order).all()
    executions = db.query(OCAPExecution).filter(OCAPExecution.ocap_id == ocap_id).all()
    root_causes = db.query(OCAPRootCause).filter(OCAPRootCause.ocap_id == ocap_id).all()
    corrective_actions = db.query(OCAPCorrectiveAction).filter(OCAPCorrectiveAction.ocap_id == ocap_id).all()
    
    wb = Workbook()
    
    header_fill = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")
    header_font_white = Font(name='微软雅黑', bold=True, size=11, color="FFFFFF")
    header_alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)
    cell_alignment = Alignment(horizontal='left', vertical='center', wrap_text=True)
    
    ws = wb.active
    ws.title = "OCAP概述"
    
    ws.merge_cells('A1:F1')
    ws['A1'] = f"OCAP - {ocap.name}"
    ws['A1'].font = Font(name='微软雅黑', bold=True, size=16)
    ws['A1'].alignment = Alignment(horizontal='center', vertical='center')
    ws.row_dimensions[1].height = 30
    
    info_data = [
        ('OCAP名称', ocap.name or ''),
        ('描述', ocap.description or ''),
        ('信号类型', ocap.signal_type or ''),
        ('优先级', PRIORITY_LABELS.get(ocap.priority, ocap.priority)),
        ('状态', STATUS_LABELS.get(ocap.status, ocap.status)),
        ('是否激活', '是' if ocap.is_active else '否'),
        ('严重性评分', str(ocap.severity_score or 1)),
        ('范围评分', str(ocap.scope_score or 1)),
        ('趋势评分', str(ocap.trend_score or 1)),
        ('综合优先级评分', str(ocap.overall_priority_score or 1)),
        ('创建人', ocap.created_by or ''),
        ('创建时间', ocap.created_at.strftime('%Y-%m-%d %H:%M') if ocap.created_at else '')
    ]
    
    for row_idx, (label, value) in enumerate(info_data, 3):
        ws.cell(row=row_idx, column=1).value = label
        ws.cell(row=row_idx, column=1).font = Font(name='微软雅黑', bold=True, size=10)
        ws.cell(row=row_idx, column=1).fill = PatternFill(start_color="E2EFDA", end_color="E2EFDA", fill_type="solid")
        ws.cell(row=row_idx, column=2).value = value
        ws.cell(row=row_idx, column=2).font = Font(name='微软雅黑', size=10)
    
    ws.column_dimensions['A'].width = 18
    ws.column_dimensions['B'].width = 40
    
    ws_steps = wb.create_sheet("步骤")
    step_headers = ['序号', '阶段', '步骤编号', '动作类型', '动作描述', '负责人角色', '负责人', '预计时长(分钟)', '是否必须']
    for col, header in enumerate(step_headers, 1):
        cell = ws_steps.cell(row=1, column=col)
        cell.value = header
        cell.font = header_font_white
        cell.fill = header_fill
        cell.alignment = header_alignment
        cell.border = thin_border
    
    for row_idx, step in enumerate(steps, 2):
        row_data = [
            row_idx - 1,
            PHASE_LABELS.get(step.phase, step.phase),
            step.step_number,
            step.action_type or '',
            step.action_description or '',
            step.responsible_role or '',
            step.responsible_person or '',
            step.expected_duration_minutes or '',
            '是' if step.is_mandatory else '否'
        ]
        for col, value in enumerate(row_data, 1):
            cell = ws_steps.cell(row=row_idx, column=col)
            cell.value = value
            cell.font = Font(name='微软雅黑', size=10)
            cell.alignment = cell_alignment
            cell.border = thin_border
    
    for col, width in enumerate([6, 10, 10, 12, 40, 15, 15, 15, 10], 1):
        ws_steps.column_dimensions[get_column_letter(col)].width = width
    
    ws_signals = wb.create_sheet("信号")
    signal_headers = ['序号', '信号时间', '信号类型', '信号值', '控制限值', '子组索引', '检测方式']
    for col, header in enumerate(signal_headers, 1):
        cell = ws_signals.cell(row=1, column=col)
        cell.value = header
        cell.font = header_font_white
        cell.fill = header_fill
        cell.alignment = header_alignment
        cell.border = thin_border
    
    for row_idx, signal in enumerate(signals, 2):
        row_data = [
            row_idx - 1,
            signal.signal_time.strftime('%Y-%m-%d %H:%M') if signal.signal_time else '',
            signal.signal_type or '',
            signal.signal_value or '',
            signal.control_limit_value or '',
            signal.subgroup_index or '',
            signal.detected_by or ''
        ]
        for col, value in enumerate(row_data, 1):
            cell = ws_signals.cell(row=row_idx, column=col)
            cell.value = value
            cell.font = Font(name='微软雅黑', size=10)
            cell.alignment = cell_alignment
            cell.border = thin_border
    
    for col, width in enumerate([6, 18, 20, 15, 15, 10, 10], 1):
        ws_signals.column_dimensions[get_column_letter(col)].width = width
    
    ws_executions = wb.create_sheet("执行记录")
    exec_headers = ['序号', '步骤ID', '状态', '开始时间', '完成时间', '执行人', '备注', '围堵措施', '产品处置']
    for col, header in enumerate(exec_headers, 1):
        cell = ws_executions.cell(row=1, column=col)
        cell.value = header
        cell.font = header_font_white
        cell.fill = header_fill
        cell.alignment = header_alignment
        cell.border = thin_border
    
    for row_idx, exec in enumerate(executions, 2):
        row_data = [
            row_idx - 1,
            exec.step_id or '',
            exec.status or '',
            exec.started_at.strftime('%Y-%m-%d %H:%M') if exec.started_at else '',
            exec.completed_at.strftime('%Y-%m-%d %H:%M') if exec.completed_at else '',
            exec.executed_by or '',
            exec.notes or '',
            exec.containment_action_taken or '',
            exec.product_disposition or ''
        ]
        for col, value in enumerate(row_data, 1):
            cell = ws_executions.cell(row=row_idx, column=col)
            cell.value = value
            cell.font = Font(name='微软雅黑', size=10)
            cell.alignment = cell_alignment
            cell.border = thin_border
    
    for col, width in enumerate([6, 10, 10, 18, 18, 12, 30, 30, 12], 1):
        ws_executions.column_dimensions[get_column_letter(col)].width = width
    
    ws_root_causes = wb.create_sheet("根本原因分析")
    rc_headers = ['序号', '分析方法', 'Why 1', 'Why 2', 'Why 3', 'Why 4', 'Why 5', '鱼骨图类别', '根本原因描述', '是否验证', '验证人']
    for col, header in enumerate(rc_headers, 1):
        cell = ws_root_causes.cell(row=1, column=col)
        cell.value = header
        cell.font = header_font_white
        cell.fill = header_fill
        cell.alignment = header_alignment
        cell.border = thin_border
    
    for row_idx, rc in enumerate(root_causes, 2):
        row_data = [
            row_idx - 1,
            rc.analysis_method or '',
            rc.why_1 or '',
            rc.why_2 or '',
            rc.why_3 or '',
            rc.why_4 or '',
            rc.why_5 or '',
            rc.fishbone_category or '',
            rc.root_cause_description or '',
            '是' if rc.verified else '否',
            rc.verified_by or ''
        ]
        for col, value in enumerate(row_data, 1):
            cell = ws_root_causes.cell(row=row_idx, column=col)
            cell.value = value
            cell.font = Font(name='微软雅黑', size=10)
            cell.alignment = cell_alignment
            cell.border = thin_border
    
    for col, width in enumerate([6, 12, 25, 25, 25, 25, 25, 12, 30, 10, 12], 1):
        ws_root_causes.column_dimensions[get_column_letter(col)].width = width
    
    ws_corrective = wb.create_sheet("纠正措施")
    ca_headers = ['序号', '根本原因ID', '措施描述', '措施类型', '负责人', '目标日期', '实际日期', '有效性验证', '验证方法', '状态']
    for col, header in enumerate(ca_headers, 1):
        cell = ws_corrective.cell(row=1, column=col)
        cell.value = header
        cell.font = header_font_white
        cell.fill = header_fill
        cell.alignment = header_alignment
        cell.border = thin_border
    
    for row_idx, ca in enumerate(corrective_actions, 2):
        row_data = [
            row_idx - 1,
            ca.root_cause_id or '',
            ca.action_description or '',
            ca.action_type or '',
            ca.responsible_person or '',
            ca.target_date.strftime('%Y-%m-%d') if ca.target_date else '',
            ca.actual_date.strftime('%Y-%m-%d') if ca.actual_date else '',
            '是' if ca.effectiveness_verified else '否',
            ca.verification_method or '',
            ca.status or ''
        ]
        for col, value in enumerate(row_data, 1):
            cell = ws_corrective.cell(row=row_idx, column=col)
            cell.value = value
            cell.font = Font(name='微软雅黑', size=10)
            cell.alignment = cell_alignment
            cell.border = thin_border
    
    for col, width in enumerate([6, 12, 40, 12, 12, 12, 12, 12, 20, 10], 1):
        ws_corrective.column_dimensions[get_column_letter(col)].width = width
    
    output = BytesIO()
    wb.save(output)
    output.seek(0)
    
    filename = f"OCAP_{ocap.name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    
    return Response(
        content=output.getvalue(),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename*=UTF-8''{filename}"}
    )
