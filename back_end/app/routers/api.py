from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from fastapi.responses import FileResponse, JSONResponse
from sqlalchemy.orm import Session
from typing import List, Optional
import os
import shutil
import json
from datetime import datetime
import asyncio
from concurrent.futures import ThreadPoolExecutor
import uuid
import torch
import requests

from ..database import get_db
from ..models.models import (
    Image, EmailSettings, User, ProductionLine, MeasurementData, AttributeData,
    ControlChartConfig, SamplingPlan, SamplingRecord, CapabilityAnalysis,
    ControlPlan, ControlPlanItem, OCAP, OCAPSignal, OCAPStep, OCAPExecution,
    OCAPRootCause, OCAPCorrectiveAction,
    MSAStudy, MSAPart, MSAOperator, MSAMeasurement, MSAResult
)
from ..schemas.schemas import (
    ImageResponse, ImageCreate, DetectionResultCreate,
    EmailSettingsResponse, EmailSettingsUpdate,
    UserCreate, UserResponse,
    MessageResponse,
    ProductionLineCreate, ProductionLineUpdate, ProductionLineResponse,
    MeasurementDataCreate, MeasurementDataResponse,
    AttributeDataCreate, AttributeDataResponse,
    ControlChartConfigCreate, ControlChartConfigUpdate, ControlChartConfigResponse,
    SamplingPlanCreate, SamplingPlanResponse,
    SamplingRecordCreate, SamplingRecordResponse,
    CapabilityAnalysisCreate, CapabilityAnalysisResponse,
    ControlPlanCreate, ControlPlanUpdate, ControlPlanResponse,
    ControlPlanItemCreate, ControlPlanItemUpdate, ControlPlanItemResponse,
    OCAPCreate, OCAPUpdate, OCAPResponse,
    OCAPSignalCreate, OCAPSignalResponse,
    OCAPStepCreate, OCAPStepUpdate, OCAPStepResponse,
    OCAPExecutionCreate, OCAPExecutionUpdate, OCAPExecutionResponse,
    OCAPRootCauseCreate, OCAPRootCauseUpdate, OCAPRootCauseResponse,
    OCAPCorrectiveActionCreate, OCAPCorrectiveActionUpdate, OCAPCorrectiveActionResponse,
    MSAStudyCreate, MSAStudyUpdate, MSAStudyResponse,
    MSAPartCreate, MSAPartUpdate, MSAPartResponse,
    MSAOperatorCreate, MSAOperatorUpdate, MSAOperatorResponse,
    MSAMeasurementCreate, MSAMeasurementUpdate, MSAMeasurementResponse,
    MSAResultResponse, MSAStudyType, MSAStudyStatus
)
from ..services.detection_service import detect_image, save_json, save_detection_result_to_db, _load_model
from ..services.control_chart_service import (
    generate_control_chart_data, 
    calculate_xbar_r_chart, 
    calculate_xbar_s_chart,
    calculate_imr_chart,
    calculate_median_r_chart,
    recommend_chart_type
)
from ..services.capability_service import (
    calculate_capability_indices,
    calculate_capability_from_raw_values,
    validate_specification_limits,
    test_normality
)
from ..services.email_service import send_control_chart_alert
from ..services.auth_service import get_password_hash
from ..services.report_service import export_control_plan_excel, export_control_plans_batch_excel, export_ocap_excel, export_control_plan_detailed_report, export_capability_analysis_report
from ..services.report_service_new import export_control_plan_html, export_capability_analysis_html, export_ocap_html

router = APIRouter(prefix="/api", tags=["api"])

last_processed_max_id = 0
last_alert_time = None


@router.get("/model-files")
async def get_model_files():
    models_dir = os.path.join(os.path.dirname(__file__), "..", "models")
    models_dir = os.path.abspath(models_dir)
    
    if not os.path.exists(models_dir):
        return {"files": []}
    
    pt_files = []
    for filename in os.listdir(models_dir):
        if filename.endswith(".pt"):
            file_path = os.path.join(models_dir, filename)
            file_size = os.path.getsize(file_path)
            pt_files.append({
                "filename": filename,
                "path": filename,
                "size": file_size,
                "size_formatted": format_file_size(file_size)
            })
    
    pt_files.sort(key=lambda x: x["filename"])
    
    return {"files": pt_files}


def format_file_size(size: int) -> str:
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size < 1024:
            return f"{size:.1f} {unit}"
        size /= 1024
    return f"{size:.1f} TB"


@router.post("/detectByImg")
async def detect_by_img(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    if not file:
        raise HTTPException(status_code=400, detail="No file provided")

    file_name, _ = os.path.splitext(file.filename)
    upload_dir = "./images"
    os.makedirs(upload_dir, exist_ok=True)
    file_path = os.path.join(upload_dir, file.filename)
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        result = detect_image(file_path, file_name)
        image_result_dir = "./static/results/images"
        json_result_dir = "./static/results/jsons"
        os.makedirs(image_result_dir, exist_ok=True)
        os.makedirs(json_result_dir, exist_ok=True)
        
        image_result_path = os.path.join(image_result_dir, f"{file_name}.png")
        save_json(result, json_result_dir, file_name)
        save_detection_result_to_db(result, db)
        
        if not os.path.exists(image_result_path):
            image_result_path = file_path
        
        from fastapi.responses import FileResponse
        return FileResponse(
            image_result_path,
            media_type="image/png",
            filename=f"{file_name}.png"
        )
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/images/batch-detect")
async def batch_detect_images(
    files: List[UploadFile] = File(...),
    line_id: int = Form(None),
    db: Session = Depends(get_db)
):
    print(f"batch_detect_images called with line_id={line_id}, files count={len(files)}")
    if not files:
        raise HTTPException(status_code=400, detail="No files provided")
    
    model_file = None
    if line_id:
        line = db.query(ProductionLine).filter(ProductionLine.id == line_id).first()
        if line and line.model_path:
            model_file = line.model_path
            print(f"Using model file: {model_file} for line {line.line_name}")
    
    allowed_extensions = {'.jpg', '.jpeg', '.png', '.tif', '.tiff', '.bmp'}
    max_file_size = 10 * 1024 * 1024
    
    upload_dir = "./images"
    os.makedirs(upload_dir, exist_ok=True)
    
    results = []
    errors = []
    
    for idx, file in enumerate(files):
        try:
            file_ext = os.path.splitext(file.filename)[1].lower()
            if file_ext not in allowed_extensions:
                errors.append({
                    "filename": file.filename,
                    "error": f"不支持的文件格式: {file_ext}"
                })
                continue
            
            file_name = os.path.splitext(file.filename)[0]
            unique_name = file_name
            file_path = os.path.join(upload_dir, f"{unique_name}{file_ext}")
            
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            
            result = detect_image(file_path, unique_name)
            
            json_result_dir = "./static/results/jsons"
            save_json(result, json_result_dir, unique_name)
            
            if line_id:
                result["line_id"] = line_id
                image_path = f"/results/images/{unique_name}.png" if result.get("hasDefects") else None
                thumbnail_path = f"/results/thumbnails/{unique_name}.png" if result.get("hasDefects") else None
                attr_data = AttributeData(
                    line_id=line_id,
                    sample_id=unique_name,
                    sample_size=1,
                    defect_count=result.get("detection_total_cnts", 0),
                    defect_details=json.dumps({
                        "image": file.filename,
                        "image_path": image_path,
                        "thumbnail_path": thumbnail_path,
                        "classes": result.get("detection_classes", []),
                        "has_defects": result.get("hasDefects", False)
                    }),
                    inspection_time=datetime.now(),
                    inspector="批量检测"
                )
                db.add(attr_data)
                print(f"Added AttributeData: line_id={line_id}, sample_id={unique_name}, defect_count={result.get('detection_total_cnts', 0)}")
            else:
                print(f"WARNING: line_id is None, skipping AttributeData save")
            
            saved_result = save_detection_result_to_db(result, db)
            
            results.append({
                "id": saved_result.id if saved_result else idx,
                "filename": f"{unique_name}.png",
                "has_defects": result.get("hasDefects", False),
                "defect_count": result.get("detection_total_cnts", 0),
                "classes": result.get("detection_classes", []),
                "image_path": f"/results/images/{unique_name}.png" if result.get("hasDefects") else None,
                "thumbnail_path": f"/results/thumbnails/{unique_name}.png" if result.get("hasDefects") else None
            })
            
        except Exception as e:
            errors.append({
                "filename": file.filename,
                "error": str(e)
            })
    
    db.commit()
    
    return {
        "success": True,
        "total": len(files),
        "processed": len(results),
        "failed": len(errors),
        "results": results,
        "errors": errors,
        "summary": {
            "total_defects": sum(r["defect_count"] for r in results),
            "images_with_defects": sum(1 for r in results if r["has_defects"])
        }
    }


@router.get("/images/batch", response_model=List[ImageResponse])
async def get_images(
    startDate: Optional[str] = None,
    endDate: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Image)
    
    if startDate and endDate:
        query = query.filter(Image.captureTime.between(startDate, endDate))
    
    images = query.all()
    
    result = [
        ImageResponse(
            id=image.id,
            name=image.name,
            hasDefects=image.hasDefects,
            detection_total_cnts=image.detection_total_cnts,
            detection_classes=image.get_detection_classes(),
            detection_boxes=image.get_detection_boxes(),
            detection_scores=image.get_detection_scores(),
            captureTime=image.captureTime
        )
        for image in images
    ]
    
    return result


@router.get("/images/{image_id}", response_model=ImageResponse)
async def get_image(image_id: int, db: Session = Depends(get_db)):
    image = db.query(Image).filter(Image.id == image_id).first()
    if not image:
        raise HTTPException(status_code=404, detail="Image not found")
    
    return ImageResponse(
        id=image.id,
        name=image.name,
        hasDefects=image.hasDefects,
        detection_total_cnts=image.detection_total_cnts,
        detection_classes=image.get_detection_classes(),
        detection_boxes=image.get_detection_boxes(),
        detection_scores=image.get_detection_scores(),
        captureTime=image.captureTime
    )


@router.post("/images", response_model=ImageResponse)
async def add_image(image_data: ImageCreate, db: Session = Depends(get_db)):
    try:
        capture_time = datetime.strptime(image_data.captureTime, '%Y-%m-%d %H:%M:%S.%f')
    except ValueError:
        capture_time = datetime.strptime(image_data.captureTime, '%Y-%m-%d %H:%M:%S')
    
    new_image = Image(
        name=image_data.name,
        hasDefects=image_data.hasDefects,
        captureTime=capture_time
    )
    db.add(new_image)
    db.commit()
    db.refresh(new_image)
    
    return ImageResponse(
        id=new_image.id,
        name=new_image.name,
        hasDefects=new_image.hasDefects,
        detection_total_cnts=new_image.detection_total_cnts,
        detection_classes=new_image.get_detection_classes(),
        detection_boxes=new_image.get_detection_boxes(),
        detection_scores=new_image.get_detection_scores(),
        captureTime=new_image.captureTime
    )


@router.post("/images/detection_results", response_model=MessageResponse)
async def save_detection_result(
    data: DetectionResultCreate,
    db: Session = Depends(get_db)
):
    try:
        capture_time = datetime.strptime(data.captureTime, '%Y-%m-%d %H:%M:%S.%f')
    except ValueError:
        capture_time = datetime.strptime(data.captureTime, '%Y-%m-%d %H:%M:%S')
    
    new_image = Image(
        name=data.name,
        hasDefects=data.hasDefects,
        captureTime=capture_time,
        detection_total_cnts=data.detection_total_cnts
    )
    new_image.set_detection_classes(data.detection_classes)
    new_image.set_detection_boxes(data.detection_boxes)
    new_image.set_detection_scores(data.detection_scores)
    
    db.add(new_image)
    db.commit()
    
    return MessageResponse(message="Detection result saved successfully.")


@router.get("/email-settings", response_model=EmailSettingsResponse)
async def get_email_settings(db: Session = Depends(get_db)):
    email_setting = db.query(EmailSettings).first()
    
    if email_setting:
        return EmailSettingsResponse(
            email=email_setting.email,
            updated_at=email_setting.updated_at
        )
    else:
        return EmailSettingsResponse(
            email="2395365918@qq.com",
            updated_at=datetime.now()
        )


@router.put("/email-settings", response_model=EmailSettingsResponse)
async def update_email_settings(
    data: EmailSettingsUpdate,
    db: Session = Depends(get_db)
):
    import re
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_pattern, data.email):
        raise HTTPException(status_code=400, detail="Invalid email format")
    
    email_setting = db.query(EmailSettings).first()
    
    if email_setting:
        email_setting.email = data.email
    else:
        email_setting = EmailSettings(email=data.email)
        db.add(email_setting)
    
    db.commit()
    db.refresh(email_setting)
    
    return EmailSettingsResponse(
        email=email_setting.email,
        updated_at=email_setting.updated_at
    )


@router.get("/users", response_model=List[UserResponse])
async def get_users(db: Session = Depends(get_db)):
    users = db.query(User).all()
    return [
        UserResponse(
            id=u.id,
            user_id=u.user_id,
            name=u.name,
            role=u.role,
            created_at=u.created_at
        )
        for u in users
    ]


@router.post("/users", response_model=UserResponse)
async def add_user(user_data: UserCreate, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.user_id == user_data.user_id).first()
    if existing:
        raise HTTPException(status_code=400, detail="User ID already exists")
    
    new_user = User(
        user_id=user_data.user_id,
        password_hash=get_password_hash(user_data.password),
        name=user_data.name,
        role=user_data.role.value
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return UserResponse(
        id=new_user.id,
        user_id=new_user.user_id,
        name=new_user.name,
        role=new_user.role,
        created_at=new_user.created_at
    )


@router.delete("/users/{user_id}")
async def delete_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    db.delete(user)
    db.commit()
    
    return {"message": "User deleted successfully"}


@router.get("/control-chart-data")
async def get_control_chart_data(db: Session = Depends(get_db)):
    global last_processed_max_id, last_alert_time
    
    from sqlalchemy import func
    
    current_max_id = db.query(func.max(Image.id)).scalar() or 0
    
    images = db.query(Image).order_by(Image.id.desc()).limit(100).all()
    
    if not images:
        raise HTTPException(status_code=404, detail="No data available")
    
    grouped = {}
    for img in images:
        group_id = (img.id - 1) // 3
        if group_id not in grouped:
            grouped[group_id] = []
        grouped[group_id].append(img)
    
    group_ids = sorted(grouped.keys(), reverse=True)
    if len(group_ids) > 25:
        group_ids = group_ids[:25]
    
    samples = [grouped[gid] for gid in group_ids]
    samples = samples[::-1]
    
    c_list = []
    n_list = []
    sample_times = []
    sample_defects_details = []
    
    for sample in samples:
        total_defects = sum(img.detection_total_cnts for img in sample)
        sample_size = len(sample)
        
        c_list.append(total_defects)
        n_list.append(float(sample_size))
        sample_times.append(sample[-1].captureTime.isoformat())
        
        defects_info = {
            'sample_size': sample_size,
            'total_defects': total_defects,
            'defects_per_pcb': [img.detection_total_cnts for img in sample],
            'pcb_names': [img.name for img in sample],
            'capture_times': [img.captureTime.isoformat() for img in sample]
        }
        sample_defects_details.append(defects_info)
    
    chart_data = generate_control_chart_data(c_list, n_list)
    
    chart_data['sample_times'] = sample_times
    chart_data['sample_defects_details'] = sample_defects_details
    chart_data['message'] = '控制图数据包含所有8个异常规则检测结果'
    
    should_send_email = False
    if chart_data['abnormal_points'] and current_max_id != last_processed_max_id:
        if last_alert_time is None:
            should_send_email = True
        else:
            from datetime import timedelta
            time_diff = datetime.now() - last_alert_time
            if time_diff > timedelta(minutes=30):
                should_send_email = True
    
    if should_send_email:
        abnormal_data = {
            'abnormal_points': chart_data['abnormal_points'],
            'abnormal_rules': chart_data['abnormal_rules'],
            'sample_defects_details': chart_data['sample_defects_details'],
            'u_list': chart_data['u_list'],
            'c_list': chart_data['c_list'],
            'n_list': chart_data['n_list'],
            'center_line': chart_data['center_line'],
            'ucl_list': chart_data['ucl_list'],
            'lcl_list': chart_data['lcl_list'],
            'statistics': chart_data['statistics']
        }
        
        email_setting = db.query(EmailSettings).first()
        recipient_email = email_setting.email if email_setting else '2395365918@qq.com'
        
        send_control_chart_alert(abnormal_data, recipient_email)
        last_processed_max_id = current_max_id
        last_alert_time = datetime.now()
    
    return chart_data


@router.get("/production-lines/{line_id}/control-chart/{chart_type}")
async def get_line_control_chart(
    line_id: int,
    chart_type: str,
    subgroup_size: Optional[int] = None,
    db: Session = Depends(get_db)
):
    line = db.query(ProductionLine).filter(ProductionLine.id == line_id).first()
    if not line:
        raise HTTPException(status_code=404, detail="产线不存在")
    
    chart_type_upper = chart_type.upper()
    
    if chart_type_upper in ['XR', 'XS', 'IMR', 'MEDIAN']:
        measurement_data = db.query(MeasurementData).filter(
            MeasurementData.line_id == line_id
        ).order_by(MeasurementData.measurement_time.desc()).limit(250).all()
        
        if not measurement_data:
            raise HTTPException(status_code=404, detail="没有足够的量值数据")
        
        if chart_type_upper == 'IMR':
            all_values = []
            for m in measurement_data[::-1]:
                values = m.get_measurement_values()
                if values:
                    all_values.extend(values)
            
            if not all_values:
                raise HTTPException(status_code=404, detail="没有有效的测量数据")
            
            chart_data = calculate_imr_chart(all_values)
        elif chart_type_upper == 'MEDIAN':
            data_groups = []
            for m in measurement_data:
                values = m.get_measurement_values()
                if values:
                    data_groups.append(values)
            
            if not data_groups:
                raise HTTPException(status_code=404, detail="没有有效的测量数据")
            
            chart_data = calculate_median_r_chart(data_groups, subgroup_size)
        else:
            data_groups = []
            for m in measurement_data:
                values = m.get_measurement_values()
                if values:
                    data_groups.append(values)
            
            if not data_groups:
                raise HTTPException(status_code=404, detail="没有有效的测量数据")
            
            if chart_type_upper == 'XR':
                chart_data = calculate_xbar_r_chart(data_groups, subgroup_size)
            else:
                chart_data = calculate_xbar_s_chart(data_groups, subgroup_size)
        
        chart_data['line_id'] = line_id
        chart_data['line_name'] = line.line_name
        chart_data['data_type'] = line.data_type
        
        return chart_data
    
    elif chart_type_upper in ['U', 'P', 'NP', 'C']:
        attr_data = db.query(AttributeData).filter(
            AttributeData.line_id == line_id
        ).order_by(AttributeData.inspection_time.desc()).limit(125).all()
        
        if not attr_data:
            raise HTTPException(status_code=404, detail="没有足够的属性数据")
        
        c_list = [d.defect_count for d in attr_data[::-1]]
        n_list = [float(d.sample_size) for d in attr_data[::-1]]
        
        chart_data = generate_control_chart_data(c_list, n_list, chart_type_upper)
        chart_data['line_id'] = line_id
        chart_data['line_name'] = line.line_name
        chart_data['data_type'] = line.data_type
        
        return chart_data
    
    else:
        raise HTTPException(status_code=400, detail=f"不支持的控制图类型: {chart_type}")


@router.get("/production-lines/{line_id}/recommend-chart")
async def get_recommended_chart_type(line_id: int, db: Session = Depends(get_db)):
    line = db.query(ProductionLine).filter(ProductionLine.id == line_id).first()
    if not line:
        raise HTTPException(status_code=404, detail="产线不存在")
    
    if line.data_type == 'attribute':
        return {
            'line_id': line_id,
            'line_name': line.line_name,
            'data_type': line.data_type,
            'recommended': 'U',
            'reason': '属性数据推荐使用U图（单位缺陷数图）',
            'alternatives': ['P', 'NP', 'C']
        }
    
    measurement_data = db.query(MeasurementData).filter(
        MeasurementData.line_id == line_id
    ).order_by(MeasurementData.measurement_time.desc()).limit(250).all()
    
    if not measurement_data:
        return {
            'line_id': line_id,
            'line_name': line.line_name,
            'data_type': line.data_type,
            'recommended': 'U',
            'reason': '没有量值数据，默认推荐U图',
            'alternatives': []
        }
    
    data_groups = []
    for m in measurement_data:
        values = m.get_measurement_values()
        if values:
            data_groups.append(values)
    
    recommendation = recommend_chart_type(data_groups, line.data_type)
    recommendation['line_id'] = line_id
    recommendation['line_name'] = line.line_name
    recommendation['data_type'] = line.data_type
    
    return recommendation


@router.post("/production-lines", response_model=ProductionLineResponse)
async def create_production_line(line_data: ProductionLineCreate, db: Session = Depends(get_db)):
    existing = db.query(ProductionLine).filter(ProductionLine.line_code == line_data.line_code).first()
    if existing:
        raise HTTPException(status_code=400, detail="产线编号已存在")
    
    if line_data.model_path:
        models_dir = os.path.join(os.path.dirname(__file__), "..", "models")
        model_full_path = os.path.join(models_dir, line_data.model_path)
        if not os.path.exists(model_full_path):
            raise HTTPException(status_code=400, detail="指定的模型文件不存在")
    
    new_line = ProductionLine(
        line_code=line_data.line_code,
        line_name=line_data.line_name,
        line_description=line_data.line_description,
        data_type=line_data.data_type.value,
        model_path=line_data.model_path,
        status=line_data.status.value
    )
    db.add(new_line)
    db.commit()
    db.refresh(new_line)
    
    return ProductionLineResponse(
        id=new_line.id,
        line_code=new_line.line_code,
        line_name=new_line.line_name,
        line_description=new_line.line_description,
        data_type=new_line.data_type,
        model_path=new_line.model_path,
        status=new_line.status,
        created_at=new_line.created_at,
        updated_at=new_line.updated_at
    )


@router.get("/production-lines", response_model=List[ProductionLineResponse])
async def get_production_lines(db: Session = Depends(get_db)):
    lines = db.query(ProductionLine).all()
    return [
        ProductionLineResponse(
            id=line.id,
            line_code=line.line_code,
            line_name=line.line_name,
            line_description=line.line_description,
            data_type=line.data_type,
            model_path=line.model_path,
            status=line.status,
            created_at=line.created_at,
            updated_at=line.updated_at
        )
        for line in lines
    ]


@router.get("/production-lines/{line_id}", response_model=ProductionLineResponse)
async def get_production_line(line_id: int, db: Session = Depends(get_db)):
    line = db.query(ProductionLine).filter(ProductionLine.id == line_id).first()
    if not line:
        raise HTTPException(status_code=404, detail="产线不存在")
    
    return ProductionLineResponse(
        id=line.id,
        line_code=line.line_code,
        line_name=line.line_name,
        line_description=line.line_description,
        data_type=line.data_type,
        model_path=line.model_path,
        status=line.status,
        created_at=line.created_at,
        updated_at=line.updated_at
    )


@router.put("/production-lines/{line_id}", response_model=ProductionLineResponse)
async def update_production_line(line_id: int, line_data: ProductionLineUpdate, db: Session = Depends(get_db)):
    line = db.query(ProductionLine).filter(ProductionLine.id == line_id).first()
    if not line:
        raise HTTPException(status_code=404, detail="产线不存在")
    
    if line_data.line_name is not None:
        line.line_name = line_data.line_name
    if line_data.line_description is not None:
        line.line_description = line_data.line_description
    if line_data.data_type is not None:
        line.data_type = line_data.data_type.value
    if line_data.model_path is not None:
        if line_data.model_path:
            models_dir = os.path.join(os.path.dirname(__file__), "..", "models")
            model_full_path = os.path.join(models_dir, line_data.model_path)
            if not os.path.exists(model_full_path):
                raise HTTPException(status_code=400, detail="指定的模型文件不存在")
        line.model_path = line_data.model_path
    if line_data.status is not None:
        line.status = line_data.status.value
    
    db.commit()
    db.refresh(line)
    
    return ProductionLineResponse(
        id=line.id,
        line_code=line.line_code,
        line_name=line.line_name,
        line_description=line.line_description,
        data_type=line.data_type,
        model_path=line.model_path,
        status=line.status,
        created_at=line.created_at,
        updated_at=line.updated_at
    )


@router.delete("/production-lines/{line_id}")
async def delete_production_line(line_id: int, db: Session = Depends(get_db)):
    line = db.query(ProductionLine).filter(ProductionLine.id == line_id).first()
    if not line:
        raise HTTPException(status_code=404, detail="产线不存在")
    
    db.delete(line)
    db.commit()
    
    return {"message": "产线删除成功"}


@router.post("/measurement-data", response_model=MeasurementDataResponse)
async def create_measurement_data(data: MeasurementDataCreate, db: Session = Depends(get_db)):
    try:
        measurement_time = datetime.strptime(data.measurement_time, '%Y-%m-%d %H:%M:%S.%f') if data.measurement_time else datetime.now()
    except ValueError:
        try:
            measurement_time = datetime.strptime(data.measurement_time, '%Y-%m-%d %H:%M:%S') if data.measurement_time else datetime.now()
        except ValueError:
            measurement_time = datetime.now()
    
    new_data = MeasurementData(
        line_id=data.line_id,
        sample_id=data.sample_id,
        measurement_values=json.dumps(data.measurement_values),
        measurement_time=measurement_time,
        operator=data.operator,
        equipment=data.equipment
    )
    db.add(new_data)
    db.commit()
    db.refresh(new_data)
    
    return MeasurementDataResponse(
        id=new_data.id,
        line_id=new_data.line_id,
        sample_id=new_data.sample_id,
        measurement_values=new_data.get_measurement_values(),
        measurement_time=new_data.measurement_time,
        operator=new_data.operator,
        equipment=new_data.equipment,
        created_at=new_data.created_at
    )


@router.get("/measurement-data", response_model=List[MeasurementDataResponse])
async def get_measurement_data(line_id: Optional[int] = None, db: Session = Depends(get_db)):
    query = db.query(MeasurementData)
    if line_id:
        query = query.filter(MeasurementData.line_id == line_id)
    
    data_list = query.order_by(MeasurementData.measurement_time.desc()).all()
    
    return [
        MeasurementDataResponse(
            id=data.id,
            line_id=data.line_id,
            sample_id=data.sample_id,
            measurement_values=data.get_measurement_values(),
            measurement_time=data.measurement_time,
            operator=data.operator,
            equipment=data.equipment,
            created_at=data.created_at
        )
        for data in data_list
    ]


@router.post("/attribute-data", response_model=AttributeDataResponse)
async def create_attribute_data(data: AttributeDataCreate, db: Session = Depends(get_db)):
    try:
        inspection_time = datetime.strptime(data.inspection_time, '%Y-%m-%d %H:%M:%S.%f') if data.inspection_time else datetime.now()
    except ValueError:
        try:
            inspection_time = datetime.strptime(data.inspection_time, '%Y-%m-%d %H:%M:%S') if data.inspection_time else datetime.now()
        except ValueError:
            inspection_time = datetime.now()
    
    new_data = AttributeData(
        line_id=data.line_id,
        sample_id=data.sample_id,
        sample_size=data.sample_size,
        defect_count=data.defect_count,
        defect_details=json.dumps(data.defect_details),
        inspection_time=inspection_time,
        inspector=data.inspector
    )
    db.add(new_data)
    db.commit()
    db.refresh(new_data)
    
    return AttributeDataResponse(
        id=new_data.id,
        line_id=new_data.line_id,
        sample_id=new_data.sample_id,
        sample_size=new_data.sample_size,
        defect_count=new_data.defect_count,
        defect_details=new_data.get_defect_details(),
        inspection_time=new_data.inspection_time,
        inspector=new_data.inspector,
        created_at=new_data.created_at
    )


@router.get("/attribute-data", response_model=List[AttributeDataResponse])
async def get_attribute_data(line_id: Optional[int] = None, db: Session = Depends(get_db)):
    query = db.query(AttributeData)
    if line_id:
        query = query.filter(AttributeData.line_id == line_id)
    
    data_list = query.order_by(AttributeData.inspection_time.desc()).all()
    
    return [
        AttributeDataResponse(
            id=data.id,
            line_id=data.line_id,
            sample_id=data.sample_id,
            sample_size=data.sample_size,
            defect_count=data.defect_count,
            defect_details=data.get_defect_details(),
            inspection_time=data.inspection_time,
            inspector=data.inspector,
            created_at=data.created_at
        )
        for data in data_list
    ]


@router.post("/control-chart-config", response_model=ControlChartConfigResponse)
async def create_control_chart_config(config_data: ControlChartConfigCreate, db: Session = Depends(get_db)):
    line = db.query(ProductionLine).filter(ProductionLine.id == config_data.line_id).first()
    if not line:
        raise HTTPException(status_code=404, detail="产线不存在")
    
    existing = db.query(ControlChartConfig).filter(ControlChartConfig.line_id == config_data.line_id).first()
    if existing:
        raise HTTPException(status_code=400, detail="该产线已存在控制图配置")
    
    new_config = ControlChartConfig(
        line_id=config_data.line_id,
        chart_type=config_data.chart_type.value,
        control_limit_type=config_data.control_limit_type.value,
        alarm_rules=json.dumps(config_data.alarm_rules)
    )
    db.add(new_config)
    db.commit()
    db.refresh(new_config)
    
    return ControlChartConfigResponse(
        id=new_config.id,
        line_id=new_config.line_id,
        chart_type=new_config.chart_type,
        control_limit_type=new_config.control_limit_type,
        alarm_rules=new_config.get_alarm_rules(),
        created_at=new_config.created_at,
        updated_at=new_config.updated_at
    )


@router.get("/control-chart-config", response_model=List[ControlChartConfigResponse])
async def get_control_chart_configs(line_id: Optional[int] = None, db: Session = Depends(get_db)):
    query = db.query(ControlChartConfig)
    if line_id:
        query = query.filter(ControlChartConfig.line_id == line_id)
    
    configs = query.all()
    
    return [
        ControlChartConfigResponse(
            id=config.id,
            line_id=config.line_id,
            chart_type=config.chart_type,
            control_limit_type=config.control_limit_type,
            alarm_rules=config.get_alarm_rules(),
            created_at=config.created_at,
            updated_at=config.updated_at
        )
        for config in configs
    ]


@router.put("/control-chart-config/{config_id}", response_model=ControlChartConfigResponse)
async def update_control_chart_config(config_id: int, config_data: ControlChartConfigUpdate, db: Session = Depends(get_db)):
    config = db.query(ControlChartConfig).filter(ControlChartConfig.id == config_id).first()
    if not config:
        raise HTTPException(status_code=404, detail="控制图配置不存在")
    
    if config_data.chart_type is not None:
        config.chart_type = config_data.chart_type.value
    if config_data.control_limit_type is not None:
        config.control_limit_type = config_data.control_limit_type.value
    if config_data.alarm_rules is not None:
        config.alarm_rules = json.dumps(config_data.alarm_rules)
    
    db.commit()
    db.refresh(config)
    
    return ControlChartConfigResponse(
        id=config.id,
        line_id=config.line_id,
        chart_type=config.chart_type,
        control_limit_type=config.control_limit_type,
        alarm_rules=config.get_alarm_rules(),
        created_at=config.created_at,
        updated_at=config.updated_at
    )


@router.post("/sampling-plans", response_model=SamplingPlanResponse)
async def create_sampling_plan(plan_data: SamplingPlanCreate, db: Session = Depends(get_db)):
    if plan_data.line_id:
        line = db.query(ProductionLine).filter(ProductionLine.id == plan_data.line_id).first()
        if not line:
            raise HTTPException(status_code=404, detail="产线不存在")
    
    new_plan = SamplingPlan(
        line_id=plan_data.line_id,
        plan_name=plan_data.plan_name,
        batch_size=plan_data.batch_size,
        aql_value=plan_data.aql_value,
        inspection_level=plan_data.inspection_level.value,
        sampling_type=plan_data.sampling_type.value
    )
    db.add(new_plan)
    db.commit()
    db.refresh(new_plan)
    
    return SamplingPlanResponse(
        id=new_plan.id,
        line_id=new_plan.line_id,
        plan_name=new_plan.plan_name,
        batch_size=new_plan.batch_size,
        aql_value=new_plan.aql_value,
        inspection_level=new_plan.inspection_level,
        sample_size=new_plan.sample_size,
        acceptance_number=new_plan.acceptance_number,
        rejection_number=new_plan.rejection_number,
        sampling_type=new_plan.sampling_type,
        created_at=new_plan.created_at
    )


@router.get("/sampling-plans", response_model=List[SamplingPlanResponse])
async def get_sampling_plans(line_id: Optional[int] = None, db: Session = Depends(get_db)):
    query = db.query(SamplingPlan)
    if line_id:
        query = query.filter(SamplingPlan.line_id == line_id)
    
    plans = query.all()
    
    return [
        SamplingPlanResponse(
            id=plan.id,
            line_id=plan.line_id,
            plan_name=plan.plan_name,
            batch_size=plan.batch_size,
            aql_value=plan.aql_value,
            inspection_level=plan.inspection_level,
            sample_size=plan.sample_size,
            acceptance_number=plan.acceptance_number,
            rejection_number=plan.rejection_number,
            sampling_type=plan.sampling_type,
            created_at=plan.created_at
        )
        for plan in plans
    ]


@router.get("/sampling-plans/{plan_id}", response_model=SamplingPlanResponse)
async def get_sampling_plan(plan_id: int, db: Session = Depends(get_db)):
    plan = db.query(SamplingPlan).filter(SamplingPlan.id == plan_id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="抽样方案不存在")
    
    return SamplingPlanResponse(
        id=plan.id,
        line_id=plan.line_id,
        plan_name=plan.plan_name,
        batch_size=plan.batch_size,
        aql_value=plan.aql_value,
        inspection_level=plan.inspection_level,
        sample_size=plan.sample_size,
        acceptance_number=plan.acceptance_number,
        rejection_number=plan.rejection_number,
        sampling_type=plan.sampling_type,
        created_at=plan.created_at
    )


@router.delete("/sampling-plans/{plan_id}")
async def delete_sampling_plan(plan_id: int, db: Session = Depends(get_db)):
    plan = db.query(SamplingPlan).filter(SamplingPlan.id == plan_id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="抽样方案不存在")
    
    db.delete(plan)
    db.commit()
    
    return {"message": "抽样方案删除成功"}


@router.post("/sampling-records", response_model=SamplingRecordResponse)
async def create_sampling_record(record_data: SamplingRecordCreate, db: Session = Depends(get_db)):
    if record_data.plan_id:
        plan = db.query(SamplingPlan).filter(SamplingPlan.id == record_data.plan_id).first()
        if not plan:
            raise HTTPException(status_code=404, detail="抽样方案不存在")
    
    if record_data.line_id:
        line = db.query(ProductionLine).filter(ProductionLine.id == record_data.line_id).first()
        if not line:
            raise HTTPException(status_code=404, detail="产线不存在")
    
    new_record = SamplingRecord(
        plan_id=record_data.plan_id,
        line_id=record_data.line_id,
        batch_id=record_data.batch_id,
        sample_size=record_data.sample_size,
        defect_count=record_data.defect_count,
        judgment=record_data.judgment,
        inspection_status=record_data.inspection_status
    )
    db.add(new_record)
    db.commit()
    db.refresh(new_record)
    
    return SamplingRecordResponse(
        id=new_record.id,
        plan_id=new_record.plan_id,
        line_id=new_record.line_id,
        batch_id=new_record.batch_id,
        sample_size=new_record.sample_size,
        defect_count=new_record.defect_count,
        judgment=new_record.judgment,
        inspection_status=new_record.inspection_status,
        created_at=new_record.created_at
    )


@router.get("/sampling-records", response_model=List[SamplingRecordResponse])
async def get_sampling_records(
    plan_id: Optional[int] = None,
    line_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    query = db.query(SamplingRecord)
    if plan_id:
        query = query.filter(SamplingRecord.plan_id == plan_id)
    if line_id:
        query = query.filter(SamplingRecord.line_id == line_id)
    
    records = query.order_by(SamplingRecord.created_at.desc()).all()
    
    return [
        SamplingRecordResponse(
            id=record.id,
            plan_id=record.plan_id,
            line_id=record.line_id,
            batch_id=record.batch_id,
            sample_size=record.sample_size,
            defect_count=record.defect_count,
            judgment=record.judgment,
            inspection_status=record.inspection_status,
            created_at=record.created_at
        )
        for record in records
    ]


@router.get("/production-lines/{line_id}/recommend-chart")
async def get_recommended_chart_type(line_id: int, db: Session = Depends(get_db)):
    line = db.query(ProductionLine).filter(ProductionLine.id == line_id).first()
    if not line:
        raise HTTPException(status_code=404, detail="产线不存在")
    
    if line.data_type == 'attribute':
        return {
            'recommended': 'U',
            'reason': '属性数据推荐使用U图（单位缺陷数图）',
            'alternatives': ['P', 'NP', 'C'],
            'data_type': line.data_type
        }
    
    measurement_data = db.query(MeasurementData).filter(
        MeasurementData.line_id == line_id
    ).order_by(MeasurementData.measurement_time.desc()).limit(250).all()
    
    if not measurement_data:
        return {
            'recommended': 'U',
            'reason': '没有量值数据，默认推荐U图',
            'alternatives': [],
            'data_type': line.data_type
        }
    
    data_groups = []
    for m in measurement_data:
        values = m.get_measurement_values()
        if values:
            data_groups.append(values)
    
    recommendation = recommend_chart_type(data_groups, line.data_type)
    recommendation['line_id'] = line_id
    recommendation['line_name'] = line.line_name
    
    recommendation['data_type'] = line.data_type
    
    return recommendation


@router.post("/capability-analysis")
async def create_capability_analysis(
    data: CapabilityAnalysisCreate,
    db: Session = Depends(get_db)
):
    line = db.query(ProductionLine).filter(ProductionLine.id == data.line_id).first()
    if not line:
        raise HTTPException(status_code=404, detail="产线不存在")
    
    if line.data_type == 'attribute':
        raise HTTPException(
            status_code=400, 
            detail="计数型数据不支持过程能力分析。过程能力分析（Cp, Cpk等）仅适用于计量型数据。"
        )
    
    if not data.data_values or len(data.data_values) < 2:
        raise HTTPException(status_code=400, detail="数据值至少需要2个样本")
    
    validation = validate_specification_limits(data.usl, data.lsl, data.data_values)
    if not validation['valid']:
        raise HTTPException(status_code=400, detail=f"规格限验证失败: {', '.join(validation['errors'])}")
    
    subgroup_size = 5
    result = calculate_capability_from_raw_values(
        values=data.data_values,
        usl=data.usl,
        lsl=data.lsl,
        target=data.target,
        sigma_machine=data.sigma_machine
    )
    
    new_analysis = CapabilityAnalysis(
        line_id=data.line_id,
        analysis_name=data.analysis_name,
        usl=str(data.usl),
        lsl=str(data.lsl),
        target=str(data.target) if data.target else None,
        cp=str(result['indices']['cp']['value']),
        cpk=str(result['indices']['cpk']['value']),
        pp=str(result['indices']['pp']['value']),
        ppk=str(result['indices']['ppk']['value']),
        cm=str(result['indices']['cm']['value']) if result['indices']['cm']['value'] else None,
        cmk=str(result['indices']['cmk']['value']) if result['indices']['cmk']['value'] else None,
        mean=str(result['mean']),
        sigma_within=str(result['sigma_within']),
        sigma_overall=str(result['sigma_overall']),
        sigma_machine=str(data.sigma_machine) if data.sigma_machine else None,
        sample_count=result['data_statistics']['total_samples'],
        subgroup_count=result['data_statistics']['subgroup_count'],
        data_values=json.dumps(data.data_values),
        status="completed",
        analysis_type=data.analysis_type.value if data.analysis_type else "process",
        analysis_time=datetime.now()
    )
    db.add(new_analysis)
    db.commit()
    db.refresh(new_analysis)
    
    result['id'] = new_analysis.id
    result['line_id'] = data.line_id
    result['line_name'] = line.line_name
    result['analysis_name'] = new_analysis.analysis_name
    result['status'] = new_analysis.status
    result['analysis_type'] = new_analysis.analysis_type
    result['analysis_time'] = new_analysis.analysis_time.isoformat()
    result['created_at'] = new_analysis.created_at.isoformat()
    
    result['cp'] = result['indices']['cp']
    result['cpk'] = result['indices']['cpk']
    result['pp'] = result['indices']['pp']
    result['ppk'] = result['indices']['ppk']
    result['cm'] = result['indices']['cm']
    result['cmk'] = result['indices']['cmk']
    
    return result


@router.get("/capability-analysis", response_model=List[CapabilityAnalysisResponse])
async def get_capability_analyses(
    line_id: Optional[int] = None,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    query = db.query(CapabilityAnalysis)
    if line_id:
        query = query.filter(CapabilityAnalysis.line_id == line_id)
    
    analyses = query.order_by(CapabilityAnalysis.analysis_time.desc()).limit(limit).all()
    
    return [
        {
            'id': a.id,
            'line_id': a.line_id,
            'analysis_name': a.analysis_name,
            'usl': a.usl,
            'lsl': a.lsl,
            'target': a.target,
            'cp': a.cp,
            'cpk': a.cpk,
            'pp': a.pp,
            'ppk': a.ppk,
            'cm': a.cm,
            'cmk': a.cmk,
            'mean': a.mean,
            'sigma_within': a.sigma_within,
            'sigma_overall': a.sigma_overall,
            'sigma_machine': a.sigma_machine,
            'sample_count': a.sample_count,
            'subgroup_count': a.subgroup_count,
            'data_values': a.get_data_values(),
            'status': a.status,
            'analysis_type': a.analysis_type,
            'analysis_time': a.analysis_time,
            'created_at': a.created_at
        }
        for a in analyses
    ]


@router.get("/capability-analysis/{analysis_id}")
async def get_capability_analysis(analysis_id: int, db: Session = Depends(get_db)):
    analysis = db.query(CapabilityAnalysis).filter(CapabilityAnalysis.id == analysis_id).first()
    if not analysis:
        raise HTTPException(status_code=404, detail="能力分析记录不存在")
    
    data_values = analysis.get_data_values()
    
    result = calculate_capability_from_raw_values(
        values=data_values,
        usl=float(analysis.usl),
        lsl=float(analysis.lsl),
        target=float(analysis.target) if analysis.target else None,
        sigma_machine=float(analysis.sigma_machine) if analysis.sigma_machine else None
    )
    
    result['id'] = analysis.id
    result['line_id'] = analysis.line_id
    result['analysis_name'] = analysis.analysis_name
    result['status'] = analysis.status
    result['analysis_type'] = analysis.analysis_type
    result['analysis_time'] = analysis.analysis_time.isoformat()
    result['created_at'] = analysis.created_at.isoformat()
    
    return result


@router.delete("/capability-analysis/{analysis_id}")
async def delete_capability_analysis(analysis_id: int, db: Session = Depends(get_db)):
    analysis = db.query(CapabilityAnalysis).filter(CapabilityAnalysis.id == analysis_id).first()
    if not analysis:
        raise HTTPException(status_code=404, detail="能力分析记录不存在")
    
    db.delete(analysis)
    db.commit()
    
    return {"message": "能力分析记录删除成功"}


@router.post("/capability-analysis/validate")
async def validate_limits(
    usl: float,
    lsl: float,
    data_values: List[float]
):
    return validate_specification_limits(usl, lsl, data_values)


@router.post("/capability-analysis/normality-test")
async def normality_test_endpoint(data_values: List[float]):
    return test_normality(data_values)


@router.post("/control-plans", response_model=ControlPlanResponse)
async def create_control_plan(plan_data: ControlPlanCreate, db: Session = Depends(get_db)):
    line = db.query(ProductionLine).filter(ProductionLine.id == plan_data.line_id).first()
    if not line:
        raise HTTPException(status_code=404, detail="产线不存在")
    
    new_plan = ControlPlan(
        line_id=plan_data.line_id,
        plan_type=plan_data.plan_type.value if plan_data.plan_type else "production",
        control_plan_number=plan_data.control_plan_number,
        part_number=plan_data.part_number,
        latest_change_level=plan_data.latest_change_level,
        part_name=plan_data.part_name,
        part_description=plan_data.part_description,
        organization_plant=plan_data.organization_plant,
        organization_code=plan_data.organization_code,
        key_contact=plan_data.key_contact,
        key_contact_phone=plan_data.key_contact_phone,
        core_team=plan_data.core_team,
        org_approval_date=plan_data.org_approval_date,
        org_approval_by=plan_data.org_approval_by,
        other_approval_date=plan_data.other_approval_date,
        other_approval_by=plan_data.other_approval_by,
        date_orig=plan_data.date_orig,
        date_rev=plan_data.date_rev,
        customer_eng_approval_date=plan_data.customer_eng_approval_date,
        customer_eng_approval_by=plan_data.customer_eng_approval_by,
        customer_quality_approval_date=plan_data.customer_quality_approval_date,
        customer_quality_approval_by=plan_data.customer_quality_approval_by,
        page_number=plan_data.page_number,
        total_pages=plan_data.total_pages,
        version=plan_data.version,
        status=plan_data.status.value if plan_data.status else "draft",
        created_by=plan_data.created_by
    )
    db.add(new_plan)
    db.commit()
    db.refresh(new_plan)
    
    if plan_data.items:
        for item_data in plan_data.items:
            new_item = ControlPlanItem(
                control_plan_id=new_plan.id,
                part_process_number=item_data.part_process_number,
                process_name=item_data.process_name,
                operation_description=item_data.operation_description,
                machine_device_jig_tools=item_data.machine_device_jig_tools,
                characteristic_no=item_data.characteristic_no,
                product_characteristic=item_data.product_characteristic,
                process_characteristic=item_data.process_characteristic,
                special_characteristic_class=item_data.special_characteristic_class,
                specification_tolerance=item_data.specification_tolerance,
                evaluation_measurement_technique=item_data.evaluation_measurement_technique,
                sample_size=item_data.sample_size,
                sample_frequency=item_data.sample_frequency,
                control_method=item_data.control_method,
                reaction_plan=item_data.reaction_plan,
                sort_order=item_data.sort_order
            )
            db.add(new_item)
        db.commit()
    
    return new_plan


@router.get("/control-plans", response_model=List[ControlPlanResponse])
async def get_control_plans(
    line_id: Optional[int] = None,
    plan_type: Optional[str] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(ControlPlan)
    if line_id:
        query = query.filter(ControlPlan.line_id == line_id)
    if plan_type:
        query = query.filter(ControlPlan.plan_type == plan_type)
    if status:
        query = query.filter(ControlPlan.status == status)
    
    plans = query.order_by(ControlPlan.created_at.desc()).all()
    
    result = []
    for plan in plans:
        items = db.query(ControlPlanItem).filter(
            ControlPlanItem.control_plan_id == plan.id
        ).order_by(ControlPlanItem.sort_order).all()
        
        plan_dict = {
            'id': plan.id,
            'line_id': plan.line_id,
            'plan_type': plan.plan_type,
            'control_plan_number': plan.control_plan_number,
            'part_number': plan.part_number,
            'latest_change_level': plan.latest_change_level,
            'part_name': plan.part_name,
            'part_description': plan.part_description,
            'organization_plant': plan.organization_plant,
            'organization_code': plan.organization_code,
            'key_contact': plan.key_contact,
            'key_contact_phone': plan.key_contact_phone,
            'core_team': plan.core_team,
            'org_approval_date': plan.org_approval_date,
            'org_approval_by': plan.org_approval_by,
            'other_approval_date': plan.other_approval_date,
            'other_approval_by': plan.other_approval_by,
            'date_orig': plan.date_orig,
            'date_rev': plan.date_rev,
            'customer_eng_approval_date': plan.customer_eng_approval_date,
            'customer_eng_approval_by': plan.customer_eng_approval_by,
            'customer_quality_approval_date': plan.customer_quality_approval_date,
            'customer_quality_approval_by': plan.customer_quality_approval_by,
            'page_number': plan.page_number,
            'total_pages': plan.total_pages,
            'version': plan.version,
            'status': plan.status,
            'created_by': plan.created_by,
            'created_at': plan.created_at,
            'updated_at': plan.updated_at,
            'items': [
                {
                    'id': item.id,
                    'control_plan_id': item.control_plan_id,
                    'part_process_number': item.part_process_number,
                    'process_name': item.process_name,
                    'operation_description': item.operation_description,
                    'machine_device_jig_tools': item.machine_device_jig_tools,
                    'characteristic_no': item.characteristic_no,
                    'product_characteristic': item.product_characteristic,
                    'process_characteristic': item.process_characteristic,
                    'special_characteristic_class': item.special_characteristic_class,
                    'specification_tolerance': item.specification_tolerance,
                    'evaluation_measurement_technique': item.evaluation_measurement_technique,
                    'sample_size': item.sample_size,
                    'sample_frequency': item.sample_frequency,
                    'control_method': item.control_method,
                    'reaction_plan': item.reaction_plan,
                    'sort_order': item.sort_order,
                    'created_at': item.created_at,
                    'updated_at': item.updated_at
                }
                for item in items
            ]
        }
        result.append(plan_dict)
    
    return result


@router.get("/control-plans/{plan_id}", response_model=ControlPlanResponse)
async def get_control_plan(plan_id: int, db: Session = Depends(get_db)):
    plan = db.query(ControlPlan).filter(ControlPlan.id == plan_id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="控制计划不存在")
    
    items = db.query(ControlPlanItem).filter(
        ControlPlanItem.control_plan_id == plan.id
    ).order_by(ControlPlanItem.sort_order).all()
    
    return {
        'id': plan.id,
        'line_id': plan.line_id,
        'plan_type': plan.plan_type,
        'control_plan_number': plan.control_plan_number,
        'part_number': plan.part_number,
        'latest_change_level': plan.latest_change_level,
        'part_name': plan.part_name,
        'part_description': plan.part_description,
        'organization_plant': plan.organization_plant,
        'organization_code': plan.organization_code,
        'key_contact': plan.key_contact,
        'key_contact_phone': plan.key_contact_phone,
        'core_team': plan.core_team,
        'org_approval_date': plan.org_approval_date,
        'org_approval_by': plan.org_approval_by,
        'other_approval_date': plan.other_approval_date,
        'other_approval_by': plan.other_approval_by,
        'date_orig': plan.date_orig,
        'date_rev': plan.date_rev,
        'customer_eng_approval_date': plan.customer_eng_approval_date,
        'customer_eng_approval_by': plan.customer_eng_approval_by,
        'customer_quality_approval_date': plan.customer_quality_approval_date,
        'customer_quality_approval_by': plan.customer_quality_approval_by,
        'page_number': plan.page_number,
        'total_pages': plan.total_pages,
        'version': plan.version,
        'status': plan.status,
        'created_by': plan.created_by,
        'created_at': plan.created_at,
        'updated_at': plan.updated_at,
        'items': [
            {
                'id': item.id,
                'control_plan_id': item.control_plan_id,
                'part_process_number': item.part_process_number,
                'process_name': item.process_name,
                'operation_description': item.operation_description,
                'machine_device_jig_tools': item.machine_device_jig_tools,
                'characteristic_no': item.characteristic_no,
                'product_characteristic': item.product_characteristic,
                'process_characteristic': item.process_characteristic,
                'special_characteristic_class': item.special_characteristic_class,
                'specification_tolerance': item.specification_tolerance,
                'evaluation_measurement_technique': item.evaluation_measurement_technique,
                'sample_size': item.sample_size,
                'sample_frequency': item.sample_frequency,
                'control_method': item.control_method,
                'reaction_plan': item.reaction_plan,
                'sort_order': item.sort_order,
                'created_at': item.created_at,
                'updated_at': item.updated_at
            }
            for item in items
        ]
    }


@router.put("/control-plans/{plan_id}", response_model=ControlPlanResponse)
async def update_control_plan(plan_id: int, plan_data: ControlPlanUpdate, db: Session = Depends(get_db)):
    plan = db.query(ControlPlan).filter(ControlPlan.id == plan_id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="控制计划不存在")
    
    if plan_data.plan_type is not None:
        plan.plan_type = plan_data.plan_type.value
    if plan_data.control_plan_number is not None:
        plan.control_plan_number = plan_data.control_plan_number
    if plan_data.part_number is not None:
        plan.part_number = plan_data.part_number
    if plan_data.latest_change_level is not None:
        plan.latest_change_level = plan_data.latest_change_level
    if plan_data.part_name is not None:
        plan.part_name = plan_data.part_name
    if plan_data.part_description is not None:
        plan.part_description = plan_data.part_description
    if plan_data.organization_plant is not None:
        plan.organization_plant = plan_data.organization_plant
    if plan_data.organization_code is not None:
        plan.organization_code = plan_data.organization_code
    if plan_data.key_contact is not None:
        plan.key_contact = plan_data.key_contact
    if plan_data.key_contact_phone is not None:
        plan.key_contact_phone = plan_data.key_contact_phone
    if plan_data.core_team is not None:
        plan.core_team = plan_data.core_team
    if plan_data.org_approval_date is not None:
        plan.org_approval_date = plan_data.org_approval_date
    if plan_data.org_approval_by is not None:
        plan.org_approval_by = plan_data.org_approval_by
    if plan_data.other_approval_date is not None:
        plan.other_approval_date = plan_data.other_approval_date
    if plan_data.other_approval_by is not None:
        plan.other_approval_by = plan_data.other_approval_by
    if plan_data.date_orig is not None:
        plan.date_orig = plan_data.date_orig
    if plan_data.date_rev is not None:
        plan.date_rev = plan_data.date_rev
    if plan_data.customer_eng_approval_date is not None:
        plan.customer_eng_approval_date = plan_data.customer_eng_approval_date
    if plan_data.customer_eng_approval_by is not None:
        plan.customer_eng_approval_by = plan_data.customer_eng_approval_by
    if plan_data.customer_quality_approval_date is not None:
        plan.customer_quality_approval_date = plan_data.customer_quality_approval_date
    if plan_data.customer_quality_approval_by is not None:
        plan.customer_quality_approval_by = plan_data.customer_quality_approval_by
    if plan_data.page_number is not None:
        plan.page_number = plan_data.page_number
    if plan_data.total_pages is not None:
        plan.total_pages = plan_data.total_pages
    if plan_data.version is not None:
        plan.version = plan_data.version
    if plan_data.status is not None:
        plan.status = plan_data.status.value
    
    db.commit()
    db.refresh(plan)
    
    return plan


@router.delete("/control-plans/{plan_id}")
async def delete_control_plan(plan_id: int, db: Session = Depends(get_db)):
    plan = db.query(ControlPlan).filter(ControlPlan.id == plan_id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="控制计划不存在")
    
    items = db.query(ControlPlanItem).filter(ControlPlanItem.control_plan_id == plan_id).all()
    for item in items:
        db.delete(item)
    
    db.delete(plan)
    db.commit()
    
    return {"message": "控制计划删除成功"}


@router.get("/control-plans/{plan_id}/export/excel")
async def export_control_plan_excel_endpoint(plan_id: int, db: Session = Depends(get_db)):
    return export_control_plan_excel(plan_id, db)


@router.post("/control-plans/export/batch")
async def export_control_plans_batch_endpoint(plan_ids: List[int], db: Session = Depends(get_db)):
    return export_control_plans_batch_excel(plan_ids, db)


@router.get("/control-plans/{plan_id}/export/report")
async def export_control_plan_report_endpoint(plan_id: int, db: Session = Depends(get_db)):
    """导出控制计划详细报告 (HTML 格式) - 旧版本"""
    return export_control_plan_detailed_report(plan_id, db)


@router.get("/control-plans/{plan_id}/export/report/html")
async def export_control_plan_html_endpoint(plan_id: int, db: Session = Depends(get_db)):
    """导出控制计划 HTML 报告 (AIAG/VDA 标准格式) - 新版本"""
    return export_control_plan_html(plan_id, db)


@router.get("/capability-analysis/{analysis_id}/export/report")
async def export_capability_report_endpoint(analysis_id: int, db: Session = Depends(get_db)):
    """导出 SPC 研究报告 (HTML 格式) - 旧版本"""
    return export_capability_analysis_report(analysis_id, db)


@router.get("/capability-analysis/{analysis_id}/export/report/html")
async def export_capability_analysis_html_endpoint(analysis_id: int, db: Session = Depends(get_db)):
    """导出过程能力分析报告 HTML (AIAG/VDA SPC 标准格式) - 新版本"""
    return export_capability_analysis_html(analysis_id, db)


@router.get("/ocaps/{ocap_id}/export/report/html")
async def export_ocap_html_endpoint(ocap_id: int, db: Session = Depends(get_db)):
    """导出 OCAP 响应计划 HTML 报告"""
    return export_ocap_html(ocap_id, db)


@router.get("/production-lines/{line_id}/control-plans", response_model=List[ControlPlanResponse])
async def get_line_control_plans(line_id: int, db: Session = Depends(get_db)):
    line = db.query(ProductionLine).filter(ProductionLine.id == line_id).first()
    if not line:
        raise HTTPException(status_code=404, detail="产线不存在")
    
    plans = db.query(ControlPlan).filter(
        ControlPlan.line_id == line_id
    ).order_by(ControlPlan.created_at.desc()).all()
    
    result = []
    for plan in plans:
        items = db.query(ControlPlanItem).filter(
            ControlPlanItem.control_plan_id == plan.id
        ).order_by(ControlPlanItem.sort_order).all()
        
        plan_dict = {
            'id': plan.id,
            'line_id': plan.line_id,
            'plan_type': plan.plan_type,
            'control_plan_number': plan.control_plan_number,
            'part_number': plan.part_number,
            'latest_change_level': plan.latest_change_level,
            'part_name': plan.part_name,
            'part_description': plan.part_description,
            'organization_plant': plan.organization_plant,
            'organization_code': plan.organization_code,
            'key_contact': plan.key_contact,
            'key_contact_phone': plan.key_contact_phone,
            'core_team': plan.core_team,
            'org_approval_date': plan.org_approval_date,
            'org_approval_by': plan.org_approval_by,
            'other_approval_date': plan.other_approval_date,
            'other_approval_by': plan.other_approval_by,
            'date_orig': plan.date_orig,
            'date_rev': plan.date_rev,
            'customer_eng_approval_date': plan.customer_eng_approval_date,
            'customer_eng_approval_by': plan.customer_eng_approval_by,
            'customer_quality_approval_date': plan.customer_quality_approval_date,
            'customer_quality_approval_by': plan.customer_quality_approval_by,
            'page_number': plan.page_number,
            'total_pages': plan.total_pages,
            'version': plan.version,
            'status': plan.status,
            'created_by': plan.created_by,
            'created_at': plan.created_at,
            'updated_at': plan.updated_at,
            'items': [
                {
                    'id': item.id,
                    'control_plan_id': item.control_plan_id,
                    'part_process_number': item.part_process_number,
                    'process_name': item.process_name,
                    'operation_description': item.operation_description,
                    'machine_device_jig_tools': item.machine_device_jig_tools,
                    'characteristic_no': item.characteristic_no,
                    'product_characteristic': item.product_characteristic,
                    'process_characteristic': item.process_characteristic,
                    'special_characteristic_class': item.special_characteristic_class,
                    'specification_tolerance': item.specification_tolerance,
                    'evaluation_measurement_technique': item.evaluation_measurement_technique,
                    'sample_size': item.sample_size,
                    'sample_frequency': item.sample_frequency,
                    'control_method': item.control_method,
                    'reaction_plan': item.reaction_plan,
                    'sort_order': item.sort_order,
                    'created_at': item.created_at,
                    'updated_at': item.updated_at
                }
                for item in items
            ]
        }
        result.append(plan_dict)
    
    return result


@router.get("/control-plans/{plan_id}/items", response_model=List[ControlPlanItemResponse])
async def get_control_plan_items(plan_id: int, db: Session = Depends(get_db)):
    plan = db.query(ControlPlan).filter(ControlPlan.id == plan_id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="控制计划不存在")
    
    items = db.query(ControlPlanItem).filter(
        ControlPlanItem.control_plan_id == plan_id
    ).order_by(ControlPlanItem.sort_order).all()
    
    return items


@router.post("/control-plans/{plan_id}/items", response_model=ControlPlanItemResponse)
async def create_control_plan_item(plan_id: int, item_data: ControlPlanItemCreate, db: Session = Depends(get_db)):
    plan = db.query(ControlPlan).filter(ControlPlan.id == plan_id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="控制计划不存在")
    
    new_item = ControlPlanItem(
        control_plan_id=plan_id,
        part_process_number=item_data.part_process_number,
        process_name=item_data.process_name,
        operation_description=item_data.operation_description,
        machine_device_jig_tools=item_data.machine_device_jig_tools,
        characteristic_no=item_data.characteristic_no,
        product_characteristic=item_data.product_characteristic,
        process_characteristic=item_data.process_characteristic,
        special_characteristic_class=item_data.special_characteristic_class,
        specification_tolerance=item_data.specification_tolerance,
        evaluation_measurement_technique=item_data.evaluation_measurement_technique,
        sample_size=item_data.sample_size,
        sample_frequency=item_data.sample_frequency,
        control_method=item_data.control_method,
        reaction_plan=item_data.reaction_plan,
        sort_order=item_data.sort_order
    )
    db.add(new_item)
    db.commit()
    db.refresh(new_item)
    
    return new_item


@router.put("/control-plans/{plan_id}/items/{item_id}", response_model=ControlPlanItemResponse)
async def update_control_plan_item(plan_id: int, item_id: int, item_data: ControlPlanItemUpdate, db: Session = Depends(get_db)):
    plan = db.query(ControlPlan).filter(ControlPlan.id == plan_id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="控制计划不存在")
    
    item = db.query(ControlPlanItem).filter(
        ControlPlanItem.id == item_id,
        ControlPlanItem.control_plan_id == plan_id
    ).first()
    if not item:
        raise HTTPException(status_code=404, detail="控制计划项目不存在")
    
    if item_data.part_process_number is not None:
        item.part_process_number = item_data.part_process_number
    if item_data.process_name is not None:
        item.process_name = item_data.process_name
    if item_data.operation_description is not None:
        item.operation_description = item_data.operation_description
    if item_data.machine_device_jig_tools is not None:
        item.machine_device_jig_tools = item_data.machine_device_jig_tools
    if item_data.characteristic_no is not None:
        item.characteristic_no = item_data.characteristic_no
    if item_data.product_characteristic is not None:
        item.product_characteristic = item_data.product_characteristic
    if item_data.process_characteristic is not None:
        item.process_characteristic = item_data.process_characteristic
    if item_data.special_characteristic_class is not None:
        item.special_characteristic_class = item_data.special_characteristic_class
    if item_data.specification_tolerance is not None:
        item.specification_tolerance = item_data.specification_tolerance
    if item_data.evaluation_measurement_technique is not None:
        item.evaluation_measurement_technique = item_data.evaluation_measurement_technique
    if item_data.sample_size is not None:
        item.sample_size = item_data.sample_size
    if item_data.sample_frequency is not None:
        item.sample_frequency = item_data.sample_frequency
    if item_data.control_method is not None:
        item.control_method = item_data.control_method
    if item_data.reaction_plan is not None:
        item.reaction_plan = item_data.reaction_plan
    if item_data.sort_order is not None:
        item.sort_order = item_data.sort_order
    
    db.commit()
    db.refresh(item)
    
    return item


@router.delete("/control-plans/{plan_id}/items/{item_id}")
async def delete_control_plan_item(plan_id: int, item_id: int, db: Session = Depends(get_db)):
    plan = db.query(ControlPlan).filter(ControlPlan.id == plan_id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="控制计划不存在")
    
    item = db.query(ControlPlanItem).filter(
        ControlPlanItem.id == item_id,
        ControlPlanItem.control_plan_id == plan_id
    ).first()
    if not item:
        raise HTTPException(status_code=404, detail="控制计划项目不存在")
    
    db.delete(item)
    db.commit()
    
    return {"message": "控制计划项目删除成功"}


# ==================== OCAP API ====================

def build_ocap_response(ocap: OCAP, db: Session) -> dict:
    signals = db.query(OCAPSignal).filter(OCAPSignal.ocap_id == ocap.id).all()
    steps = db.query(OCAPStep).filter(OCAPStep.ocap_id == ocap.id).order_by(OCAPStep.sort_order).all()
    executions = db.query(OCAPExecution).filter(OCAPExecution.ocap_id == ocap.id).all()
    root_causes = db.query(OCAPRootCause).filter(OCAPRootCause.ocap_id == ocap.id).all()
    corrective_actions = db.query(OCAPCorrectiveAction).filter(OCAPCorrectiveAction.ocap_id == ocap.id).all()
    
    return {
        'id': ocap.id,
        'control_chart_config_id': ocap.control_chart_config_id,
        'line_id': ocap.line_id,
        'name': ocap.name,
        'description': ocap.description,
        'signal_type': ocap.signal_type,
        'priority': ocap.priority,
        'severity_score': ocap.severity_score,
        'scope_score': ocap.scope_score,
        'trend_score': ocap.trend_score,
        'overall_priority_score': ocap.overall_priority_score,
        'status': ocap.status,
        'is_active': ocap.is_active,
        'created_by': ocap.created_by,
        'created_at': ocap.created_at,
        'updated_at': ocap.updated_at,
        'signals': [
            {
                'id': s.id,
                'ocap_id': s.ocap_id,
                'signal_time': s.signal_time,
                'signal_type': s.signal_type,
                'signal_value': s.signal_value,
                'control_limit_value': s.control_limit_value,
                'subgroup_index': s.subgroup_index,
                'raw_data_snapshot': s.get_raw_data_snapshot() if hasattr(s, 'get_raw_data_snapshot') else {},
                'chart_snapshot_url': s.chart_snapshot_url,
                'detected_by': s.detected_by,
                'created_at': s.created_at
            }
            for s in signals
        ],
        'steps': [
            {
                'id': st.id,
                'ocap_id': st.ocap_id,
                'phase': st.phase,
                'step_number': st.step_number,
                'action_type': st.action_type,
                'action_description': st.action_description,
                'responsible_role': st.responsible_role,
                'responsible_person': st.responsible_person,
                'expected_duration_minutes': st.expected_duration_minutes,
                'deadline': st.deadline,
                'is_mandatory': st.is_mandatory,
                'prerequisites': st.get_prerequisites() if hasattr(st, 'get_prerequisites') else [],
                'sort_order': st.sort_order,
                'created_at': st.created_at,
                'updated_at': st.updated_at
            }
            for st in steps
        ],
        'executions': [
            {
                'id': e.id,
                'ocap_id': e.ocap_id,
                'step_id': e.step_id,
                'status': e.status,
                'started_at': e.started_at,
                'completed_at': e.completed_at,
                'executed_by': e.executed_by,
                'notes': e.notes,
                'evidence_urls': e.get_evidence_urls() if hasattr(e, 'get_evidence_urls') else [],
                'containment_action_taken': e.containment_action_taken,
                'product_disposition': e.product_disposition,
                'created_at': e.created_at,
                'updated_at': e.updated_at
            }
            for e in executions
        ],
        'root_causes': [
            {
                'id': rc.id,
                'ocap_id': rc.ocap_id,
                'analysis_method': rc.analysis_method,
                'why_1': rc.why_1,
                'why_2': rc.why_2,
                'why_3': rc.why_3,
                'why_4': rc.why_4,
                'why_5': rc.why_5,
                'fishbone_category': rc.fishbone_category,
                'root_cause_description': rc.root_cause_description,
                'contributing_factors': rc.get_contributing_factors() if hasattr(rc, 'get_contributing_factors') else [],
                'evidence_collected': rc.get_evidence_collected() if hasattr(rc, 'get_evidence_collected') else {},
                'verified': rc.verified,
                'verified_by': rc.verified_by,
                'verified_at': rc.verified_at,
                'created_at': rc.created_at,
                'updated_at': rc.updated_at
            }
            for rc in root_causes
        ],
        'corrective_actions': [
            {
                'id': ca.id,
                'ocap_id': ca.ocap_id,
                'root_cause_id': ca.root_cause_id,
                'action_description': ca.action_description,
                'action_type': ca.action_type,
                'responsible_person': ca.responsible_person,
                'target_date': ca.target_date,
                'actual_date': ca.actual_date,
                'effectiveness_verified': ca.effectiveness_verified,
                'verification_method': ca.verification_method,
                'verification_result': ca.verification_result,
                'status': ca.status,
                'created_at': ca.created_at,
                'updated_at': ca.updated_at
            }
            for ca in corrective_actions
        ]
    }


@router.post("/ocaps", response_model=OCAPResponse)
async def create_ocap(ocap_data: OCAPCreate, db: Session = Depends(get_db)):
    new_ocap = OCAP(
        control_chart_config_id=ocap_data.control_chart_config_id,
        line_id=ocap_data.line_id,
        name=ocap_data.name,
        description=ocap_data.description,
        signal_type=ocap_data.signal_type.value if ocap_data.signal_type else None,
        priority=ocap_data.priority.value if ocap_data.priority else "medium",
        severity_score=ocap_data.severity_score,
        scope_score=ocap_data.scope_score,
        trend_score=ocap_data.trend_score,
        overall_priority_score=ocap_data.overall_priority_score,
        status=ocap_data.status.value if ocap_data.status else "draft",
        is_active=ocap_data.is_active,
        created_by=ocap_data.created_by
    )
    db.add(new_ocap)
    db.commit()
    db.refresh(new_ocap)
    
    if ocap_data.signals:
        for signal_data in ocap_data.signals:
            new_signal = OCAPSignal(
                ocap_id=new_ocap.id,
                signal_time=signal_data.signal_time,
                signal_type=signal_data.signal_type.value if signal_data.signal_type else None,
                signal_value=signal_data.signal_value,
                control_limit_value=signal_data.control_limit_value,
                subgroup_index=signal_data.subgroup_index,
                raw_data_snapshot=json.dumps(signal_data.raw_data_snapshot) if signal_data.raw_data_snapshot else None,
                chart_snapshot_url=signal_data.chart_snapshot_url,
                detected_by=signal_data.detected_by
            )
            db.add(new_signal)
    
    if ocap_data.steps:
        for step_data in ocap_data.steps:
            new_step = OCAPStep(
                ocap_id=new_ocap.id,
                phase=step_data.phase.value if step_data.phase else "containment",
                step_number=step_data.step_number,
                action_type=step_data.action_type.value if step_data.action_type else "immediate",
                action_description=step_data.action_description,
                responsible_role=step_data.responsible_role,
                responsible_person=step_data.responsible_person,
                expected_duration_minutes=step_data.expected_duration_minutes,
                deadline=step_data.deadline,
                is_mandatory=step_data.is_mandatory,
                prerequisites=json.dumps(step_data.prerequisites) if step_data.prerequisites else None,
                sort_order=step_data.sort_order
            )
            db.add(new_step)
    
    db.commit()
    
    return build_ocap_response(new_ocap, db)


@router.get("/ocaps", response_model=List[OCAPResponse])
async def get_ocaps(
    control_chart_config_id: Optional[int] = None,
    line_id: Optional[int] = None,
    status: Optional[str] = None,
    priority: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(OCAP)
    if control_chart_config_id:
        query = query.filter(OCAP.control_chart_config_id == control_chart_config_id)
    if line_id:
        query = query.filter(OCAP.line_id == line_id)
    if status:
        query = query.filter(OCAP.status == status)
    if priority:
        query = query.filter(OCAP.priority == priority)
    
    ocaps = query.order_by(OCAP.created_at.desc()).all()
    
    return [build_ocap_response(ocap, db) for ocap in ocaps]


@router.get("/ocaps/{ocap_id}", response_model=OCAPResponse)
async def get_ocap(ocap_id: int, db: Session = Depends(get_db)):
    ocap = db.query(OCAP).filter(OCAP.id == ocap_id).first()
    if not ocap:
        raise HTTPException(status_code=404, detail="OCAP不存在")
    
    return build_ocap_response(ocap, db)


@router.put("/ocaps/{ocap_id}", response_model=OCAPResponse)
async def update_ocap(ocap_id: int, ocap_data: OCAPUpdate, db: Session = Depends(get_db)):
    ocap = db.query(OCAP).filter(OCAP.id == ocap_id).first()
    if not ocap:
        raise HTTPException(status_code=404, detail="OCAP不存在")
    
    if ocap_data.name is not None:
        ocap.name = ocap_data.name
    if ocap_data.description is not None:
        ocap.description = ocap_data.description
    if ocap_data.signal_type is not None:
        ocap.signal_type = ocap_data.signal_type.value
    if ocap_data.priority is not None:
        ocap.priority = ocap_data.priority.value
    if ocap_data.severity_score is not None:
        ocap.severity_score = ocap_data.severity_score
    if ocap_data.scope_score is not None:
        ocap.scope_score = ocap_data.scope_score
    if ocap_data.trend_score is not None:
        ocap.trend_score = ocap_data.trend_score
    if ocap_data.overall_priority_score is not None:
        ocap.overall_priority_score = ocap_data.overall_priority_score
    if ocap_data.status is not None:
        ocap.status = ocap_data.status.value
    if ocap_data.is_active is not None:
        ocap.is_active = ocap_data.is_active
    
    db.commit()
    db.refresh(ocap)
    
    return build_ocap_response(ocap, db)


@router.delete("/ocaps/{ocap_id}")
async def delete_ocap(ocap_id: int, db: Session = Depends(get_db)):
    ocap = db.query(OCAP).filter(OCAP.id == ocap_id).first()
    if not ocap:
        raise HTTPException(status_code=404, detail="OCAP不存在")
    
    db.query(OCAPCorrectiveAction).filter(OCAPCorrectiveAction.ocap_id == ocap_id).delete()
    db.query(OCAPRootCause).filter(OCAPRootCause.ocap_id == ocap_id).delete()
    db.query(OCAPExecution).filter(OCAPExecution.ocap_id == ocap_id).delete()
    db.query(OCAPStep).filter(OCAPStep.ocap_id == ocap_id).delete()
    db.query(OCAPSignal).filter(OCAPSignal.ocap_id == ocap_id).delete()
    
    db.delete(ocap)
    db.commit()
    
    return {"message": "OCAP删除成功"}


@router.get("/ocaps/{ocap_id}/export/excel")
async def export_ocap_excel_endpoint(ocap_id: int, db: Session = Depends(get_db)):
    return export_ocap_excel(ocap_id, db)


@router.get("/control-chart-configs/{config_id}/ocaps", response_model=List[OCAPResponse])
async def get_config_ocaps(config_id: int, db: Session = Depends(get_db)):
    config = db.query(ControlChartConfig).filter(ControlChartConfig.id == config_id).first()
    if not config:
        raise HTTPException(status_code=404, detail="控制图配置不存在")
    
    ocaps = db.query(OCAP).filter(
        OCAP.control_chart_config_id == config_id
    ).order_by(OCAP.created_at.desc()).all()
    
    return [build_ocap_response(ocap, db) for ocap in ocaps]


# ==================== OCAP Signal API ====================

@router.get("/ocaps/{ocap_id}/signals", response_model=List[OCAPSignalResponse])
async def get_ocap_signals(ocap_id: int, db: Session = Depends(get_db)):
    ocap = db.query(OCAP).filter(OCAP.id == ocap_id).first()
    if not ocap:
        raise HTTPException(status_code=404, detail="OCAP不存在")
    
    signals = db.query(OCAPSignal).filter(OCAPSignal.ocap_id == ocap_id).all()
    
    return [
        {
            'id': s.id,
            'ocap_id': s.ocap_id,
            'signal_time': s.signal_time,
            'signal_type': s.signal_type,
            'signal_value': s.signal_value,
            'control_limit_value': s.control_limit_value,
            'subgroup_index': s.subgroup_index,
            'raw_data_snapshot': s.get_raw_data_snapshot() if hasattr(s, 'get_raw_data_snapshot') else {},
            'chart_snapshot_url': s.chart_snapshot_url,
            'detected_by': s.detected_by,
            'created_at': s.created_at
        }
        for s in signals
    ]


@router.post("/ocaps/{ocap_id}/signals", response_model=OCAPSignalResponse)
async def create_ocap_signal(ocap_id: int, signal_data: OCAPSignalCreate, db: Session = Depends(get_db)):
    ocap = db.query(OCAP).filter(OCAP.id == ocap_id).first()
    if not ocap:
        raise HTTPException(status_code=404, detail="OCAP不存在")
    
    new_signal = OCAPSignal(
        ocap_id=ocap_id,
        signal_time=signal_data.signal_time,
        signal_type=signal_data.signal_type.value if signal_data.signal_type else None,
        signal_value=signal_data.signal_value,
        control_limit_value=signal_data.control_limit_value,
        subgroup_index=signal_data.subgroup_index,
        raw_data_snapshot=json.dumps(signal_data.raw_data_snapshot) if signal_data.raw_data_snapshot else None,
        chart_snapshot_url=signal_data.chart_snapshot_url,
        detected_by=signal_data.detected_by
    )
    db.add(new_signal)
    db.commit()
    db.refresh(new_signal)
    
    return {
        'id': new_signal.id,
        'ocap_id': new_signal.ocap_id,
        'signal_time': new_signal.signal_time,
        'signal_type': new_signal.signal_type,
        'signal_value': new_signal.signal_value,
        'control_limit_value': new_signal.control_limit_value,
        'subgroup_index': new_signal.subgroup_index,
        'raw_data_snapshot': new_signal.get_raw_data_snapshot() if hasattr(new_signal, 'get_raw_data_snapshot') else {},
        'chart_snapshot_url': new_signal.chart_snapshot_url,
        'detected_by': new_signal.detected_by,
        'created_at': new_signal.created_at
    }


@router.delete("/ocaps/{ocap_id}/signals/{signal_id}")
async def delete_ocap_signal(ocap_id: int, signal_id: int, db: Session = Depends(get_db)):
    ocap = db.query(OCAP).filter(OCAP.id == ocap_id).first()
    if not ocap:
        raise HTTPException(status_code=404, detail="OCAP不存在")
    
    signal = db.query(OCAPSignal).filter(
        OCAPSignal.id == signal_id,
        OCAPSignal.ocap_id == ocap_id
    ).first()
    if not signal:
        raise HTTPException(status_code=404, detail="OCAP信号不存在")
    
    db.delete(signal)
    db.commit()
    
    return {"message": "OCAP信号删除成功"}


# ==================== OCAP Step API ====================

@router.get("/ocaps/{ocap_id}/steps", response_model=List[OCAPStepResponse])
async def get_ocap_steps(ocap_id: int, db: Session = Depends(get_db)):
    ocap = db.query(OCAP).filter(OCAP.id == ocap_id).first()
    if not ocap:
        raise HTTPException(status_code=404, detail="OCAP不存在")
    
    steps = db.query(OCAPStep).filter(OCAPStep.ocap_id == ocap_id).order_by(OCAPStep.sort_order).all()
    
    return [
        {
            'id': s.id,
            'ocap_id': s.ocap_id,
            'phase': s.phase,
            'step_number': s.step_number,
            'action_type': s.action_type,
            'action_description': s.action_description,
            'responsible_role': s.responsible_role,
            'responsible_person': s.responsible_person,
            'expected_duration_minutes': s.expected_duration_minutes,
            'deadline': s.deadline,
            'is_mandatory': s.is_mandatory,
            'prerequisites': s.get_prerequisites() if hasattr(s, 'get_prerequisites') else [],
            'sort_order': s.sort_order,
            'created_at': s.created_at,
            'updated_at': s.updated_at
        }
        for s in steps
    ]


@router.post("/ocaps/{ocap_id}/steps", response_model=OCAPStepResponse)
async def create_ocap_step(ocap_id: int, step_data: OCAPStepCreate, db: Session = Depends(get_db)):
    ocap = db.query(OCAP).filter(OCAP.id == ocap_id).first()
    if not ocap:
        raise HTTPException(status_code=404, detail="OCAP不存在")
    
    new_step = OCAPStep(
        ocap_id=ocap_id,
        phase=step_data.phase.value if step_data.phase else "containment",
        step_number=step_data.step_number,
        action_type=step_data.action_type.value if step_data.action_type else "immediate",
        action_description=step_data.action_description,
        responsible_role=step_data.responsible_role,
        responsible_person=step_data.responsible_person,
        expected_duration_minutes=step_data.expected_duration_minutes,
        deadline=step_data.deadline,
        is_mandatory=step_data.is_mandatory,
        prerequisites=json.dumps(step_data.prerequisites) if step_data.prerequisites else None,
        sort_order=step_data.sort_order
    )
    db.add(new_step)
    db.commit()
    db.refresh(new_step)
    
    return {
        'id': new_step.id,
        'ocap_id': new_step.ocap_id,
        'phase': new_step.phase,
        'step_number': new_step.step_number,
        'action_type': new_step.action_type,
        'action_description': new_step.action_description,
        'responsible_role': new_step.responsible_role,
        'responsible_person': new_step.responsible_person,
        'expected_duration_minutes': new_step.expected_duration_minutes,
        'deadline': new_step.deadline,
        'is_mandatory': new_step.is_mandatory,
        'prerequisites': new_step.get_prerequisites() if hasattr(new_step, 'get_prerequisites') else [],
        'sort_order': new_step.sort_order,
        'created_at': new_step.created_at,
        'updated_at': new_step.updated_at
    }


@router.put("/ocaps/{ocap_id}/steps/{step_id}", response_model=OCAPStepResponse)
async def update_ocap_step(ocap_id: int, step_id: int, step_data: OCAPStepUpdate, db: Session = Depends(get_db)):
    ocap = db.query(OCAP).filter(OCAP.id == ocap_id).first()
    if not ocap:
        raise HTTPException(status_code=404, detail="OCAP不存在")
    
    step = db.query(OCAPStep).filter(
        OCAPStep.id == step_id,
        OCAPStep.ocap_id == ocap_id
    ).first()
    if not step:
        raise HTTPException(status_code=404, detail="OCAP步骤不存在")
    
    if step_data.phase is not None:
        step.phase = step_data.phase.value
    if step_data.step_number is not None:
        step.step_number = step_data.step_number
    if step_data.action_type is not None:
        step.action_type = step_data.action_type.value
    if step_data.action_description is not None:
        step.action_description = step_data.action_description
    if step_data.responsible_role is not None:
        step.responsible_role = step_data.responsible_role
    if step_data.responsible_person is not None:
        step.responsible_person = step_data.responsible_person
    if step_data.expected_duration_minutes is not None:
        step.expected_duration_minutes = step_data.expected_duration_minutes
    if step_data.deadline is not None:
        step.deadline = step_data.deadline
    if step_data.is_mandatory is not None:
        step.is_mandatory = step_data.is_mandatory
    if step_data.prerequisites is not None:
        step.prerequisites = json.dumps(step_data.prerequisites)
    if step_data.sort_order is not None:
        step.sort_order = step_data.sort_order
    
    db.commit()
    db.refresh(step)
    
    return {
        'id': step.id,
        'ocap_id': step.ocap_id,
        'phase': step.phase,
        'step_number': step.step_number,
        'action_type': step.action_type,
        'action_description': step.action_description,
        'responsible_role': step.responsible_role,
        'responsible_person': step.responsible_person,
        'expected_duration_minutes': step.expected_duration_minutes,
        'deadline': step.deadline,
        'is_mandatory': step.is_mandatory,
        'prerequisites': step.get_prerequisites() if hasattr(step, 'get_prerequisites') else [],
        'sort_order': step.sort_order,
        'created_at': step.created_at,
        'updated_at': step.updated_at
    }


@router.delete("/ocaps/{ocap_id}/steps/{step_id}")
async def delete_ocap_step(ocap_id: int, step_id: int, db: Session = Depends(get_db)):
    ocap = db.query(OCAP).filter(OCAP.id == ocap_id).first()
    if not ocap:
        raise HTTPException(status_code=404, detail="OCAP不存在")
    
    step = db.query(OCAPStep).filter(
        OCAPStep.id == step_id,
        OCAPStep.ocap_id == ocap_id
    ).first()
    if not step:
        raise HTTPException(status_code=404, detail="OCAP步骤不存在")
    
    db.delete(step)
    db.commit()
    
    return {"message": "OCAP步骤删除成功"}


# ==================== OCAP Execution API ====================

@router.get("/ocaps/{ocap_id}/executions", response_model=List[OCAPExecutionResponse])
async def get_ocap_executions(ocap_id: int, db: Session = Depends(get_db)):
    ocap = db.query(OCAP).filter(OCAP.id == ocap_id).first()
    if not ocap:
        raise HTTPException(status_code=404, detail="OCAP不存在")
    
    executions = db.query(OCAPExecution).filter(OCAPExecution.ocap_id == ocap_id).all()
    
    return [
        {
            'id': e.id,
            'ocap_id': e.ocap_id,
            'step_id': e.step_id,
            'status': e.status,
            'started_at': e.started_at,
            'completed_at': e.completed_at,
            'executed_by': e.executed_by,
            'notes': e.notes,
            'evidence_urls': e.get_evidence_urls() if hasattr(e, 'get_evidence_urls') else [],
            'containment_action_taken': e.containment_action_taken,
            'product_disposition': e.product_disposition,
            'created_at': e.created_at,
            'updated_at': e.updated_at
        }
        for e in executions
    ]


@router.post("/ocaps/{ocap_id}/executions", response_model=OCAPExecutionResponse)
async def create_ocap_execution(ocap_id: int, exec_data: OCAPExecutionCreate, db: Session = Depends(get_db)):
    ocap = db.query(OCAP).filter(OCAP.id == ocap_id).first()
    if not ocap:
        raise HTTPException(status_code=404, detail="OCAP不存在")
    
    if exec_data.step_id:
        step = db.query(OCAPStep).filter(OCAPStep.id == exec_data.step_id).first()
        if not step:
            raise HTTPException(status_code=404, detail="OCAP步骤不存在")
    
    new_execution = OCAPExecution(
        ocap_id=ocap_id,
        step_id=exec_data.step_id,
        status=exec_data.status.value if exec_data.status else "pending",
        started_at=exec_data.started_at,
        completed_at=exec_data.completed_at,
        executed_by=exec_data.executed_by,
        notes=exec_data.notes,
        evidence_urls=json.dumps(exec_data.evidence_urls) if exec_data.evidence_urls else None,
        containment_action_taken=exec_data.containment_action_taken,
        product_disposition=exec_data.product_disposition.value if exec_data.product_disposition else None
    )
    db.add(new_execution)
    db.commit()
    db.refresh(new_execution)
    
    return {
        'id': new_execution.id,
        'ocap_id': new_execution.ocap_id,
        'step_id': new_execution.step_id,
        'status': new_execution.status,
        'started_at': new_execution.started_at,
        'completed_at': new_execution.completed_at,
        'executed_by': new_execution.executed_by,
        'notes': new_execution.notes,
        'evidence_urls': new_execution.get_evidence_urls() if hasattr(new_execution, 'get_evidence_urls') else [],
        'containment_action_taken': new_execution.containment_action_taken,
        'product_disposition': new_execution.product_disposition,
        'created_at': new_execution.created_at,
        'updated_at': new_execution.updated_at
    }


@router.put("/ocaps/{ocap_id}/executions/{exec_id}", response_model=OCAPExecutionResponse)
async def update_ocap_execution(ocap_id: int, exec_id: int, exec_data: OCAPExecutionUpdate, db: Session = Depends(get_db)):
    ocap = db.query(OCAP).filter(OCAP.id == ocap_id).first()
    if not ocap:
        raise HTTPException(status_code=404, detail="OCAP不存在")
    
    execution = db.query(OCAPExecution).filter(
        OCAPExecution.id == exec_id,
        OCAPExecution.ocap_id == ocap_id
    ).first()
    if not execution:
        raise HTTPException(status_code=404, detail="OCAP执行记录不存在")
    
    if exec_data.step_id is not None:
        execution.step_id = exec_data.step_id
    if exec_data.status is not None:
        execution.status = exec_data.status.value
    if exec_data.started_at is not None:
        execution.started_at = exec_data.started_at
    if exec_data.completed_at is not None:
        execution.completed_at = exec_data.completed_at
    if exec_data.executed_by is not None:
        execution.executed_by = exec_data.executed_by
    if exec_data.notes is not None:
        execution.notes = exec_data.notes
    if exec_data.evidence_urls is not None:
        execution.evidence_urls = json.dumps(exec_data.evidence_urls)
    if exec_data.containment_action_taken is not None:
        execution.containment_action_taken = exec_data.containment_action_taken
    if exec_data.product_disposition is not None:
        execution.product_disposition = exec_data.product_disposition.value
    
    db.commit()
    db.refresh(execution)
    
    return {
        'id': execution.id,
        'ocap_id': execution.ocap_id,
        'step_id': execution.step_id,
        'status': execution.status,
        'started_at': execution.started_at,
        'completed_at': execution.completed_at,
        'executed_by': execution.executed_by,
        'notes': execution.notes,
        'evidence_urls': execution.get_evidence_urls() if hasattr(execution, 'get_evidence_urls') else [],
        'containment_action_taken': execution.containment_action_taken,
        'product_disposition': execution.product_disposition,
        'created_at': execution.created_at,
        'updated_at': execution.updated_at
    }


@router.delete("/ocaps/{ocap_id}/executions/{exec_id}")
async def delete_ocap_execution(ocap_id: int, exec_id: int, db: Session = Depends(get_db)):
    ocap = db.query(OCAP).filter(OCAP.id == ocap_id).first()
    if not ocap:
        raise HTTPException(status_code=404, detail="OCAP不存在")
    
    execution = db.query(OCAPExecution).filter(
        OCAPExecution.id == exec_id,
        OCAPExecution.ocap_id == ocap_id
    ).first()
    if not execution:
        raise HTTPException(status_code=404, detail="OCAP执行记录不存在")
    
    db.delete(execution)
    db.commit()
    
    return {"message": "OCAP执行记录删除成功"}


# ==================== OCAP Root Cause API ====================

@router.get("/ocaps/{ocap_id}/root-causes", response_model=List[OCAPRootCauseResponse])
async def get_ocap_root_causes(ocap_id: int, db: Session = Depends(get_db)):
    ocap = db.query(OCAP).filter(OCAP.id == ocap_id).first()
    if not ocap:
        raise HTTPException(status_code=404, detail="OCAP不存在")
    
    root_causes = db.query(OCAPRootCause).filter(OCAPRootCause.ocap_id == ocap_id).all()
    
    return [
        {
            'id': rc.id,
            'ocap_id': rc.ocap_id,
            'analysis_method': rc.analysis_method,
            'why_1': rc.why_1,
            'why_2': rc.why_2,
            'why_3': rc.why_3,
            'why_4': rc.why_4,
            'why_5': rc.why_5,
            'fishbone_category': rc.fishbone_category,
            'root_cause_description': rc.root_cause_description,
            'contributing_factors': rc.get_contributing_factors() if hasattr(rc, 'get_contributing_factors') else [],
            'evidence_collected': rc.get_evidence_collected() if hasattr(rc, 'get_evidence_collected') else {},
            'verified': rc.verified,
            'verified_by': rc.verified_by,
            'verified_at': rc.verified_at,
            'created_at': rc.created_at,
            'updated_at': rc.updated_at
        }
        for rc in root_causes
    ]


@router.post("/ocaps/{ocap_id}/root-causes", response_model=OCAPRootCauseResponse)
async def create_ocap_root_cause(ocap_id: int, rc_data: OCAPRootCauseCreate, db: Session = Depends(get_db)):
    ocap = db.query(OCAP).filter(OCAP.id == ocap_id).first()
    if not ocap:
        raise HTTPException(status_code=404, detail="OCAP不存在")
    
    new_root_cause = OCAPRootCause(
        ocap_id=ocap_id,
        analysis_method=rc_data.analysis_method.value if rc_data.analysis_method else "5whys",
        why_1=rc_data.why_1,
        why_2=rc_data.why_2,
        why_3=rc_data.why_3,
        why_4=rc_data.why_4,
        why_5=rc_data.why_5,
        fishbone_category=rc_data.fishbone_category,
        root_cause_description=rc_data.root_cause_description,
        contributing_factors=json.dumps(rc_data.contributing_factors) if rc_data.contributing_factors else None,
        evidence_collected=json.dumps(rc_data.evidence_collected) if rc_data.evidence_collected else None,
        verified=rc_data.verified,
        verified_by=rc_data.verified_by,
        verified_at=rc_data.verified_at
    )
    db.add(new_root_cause)
    db.commit()
    db.refresh(new_root_cause)
    
    return {
        'id': new_root_cause.id,
        'ocap_id': new_root_cause.ocap_id,
        'analysis_method': new_root_cause.analysis_method,
        'why_1': new_root_cause.why_1,
        'why_2': new_root_cause.why_2,
        'why_3': new_root_cause.why_3,
        'why_4': new_root_cause.why_4,
        'why_5': new_root_cause.why_5,
        'fishbone_category': new_root_cause.fishbone_category,
        'root_cause_description': new_root_cause.root_cause_description,
        'contributing_factors': new_root_cause.get_contributing_factors() if hasattr(new_root_cause, 'get_contributing_factors') else [],
        'evidence_collected': new_root_cause.get_evidence_collected() if hasattr(new_root_cause, 'get_evidence_collected') else {},
        'verified': new_root_cause.verified,
        'verified_by': new_root_cause.verified_by,
        'verified_at': new_root_cause.verified_at,
        'created_at': new_root_cause.created_at,
        'updated_at': new_root_cause.updated_at
    }


@router.put("/ocaps/{ocap_id}/root-causes/{rc_id}", response_model=OCAPRootCauseResponse)
async def update_ocap_root_cause(ocap_id: int, rc_id: int, rc_data: OCAPRootCauseUpdate, db: Session = Depends(get_db)):
    ocap = db.query(OCAP).filter(OCAP.id == ocap_id).first()
    if not ocap:
        raise HTTPException(status_code=404, detail="OCAP不存在")
    
    root_cause = db.query(OCAPRootCause).filter(
        OCAPRootCause.id == rc_id,
        OCAPRootCause.ocap_id == ocap_id
    ).first()
    if not root_cause:
        raise HTTPException(status_code=404, detail="根本原因分析不存在")
    
    if rc_data.analysis_method is not None:
        root_cause.analysis_method = rc_data.analysis_method.value
    if rc_data.why_1 is not None:
        root_cause.why_1 = rc_data.why_1
    if rc_data.why_2 is not None:
        root_cause.why_2 = rc_data.why_2
    if rc_data.why_3 is not None:
        root_cause.why_3 = rc_data.why_3
    if rc_data.why_4 is not None:
        root_cause.why_4 = rc_data.why_4
    if rc_data.why_5 is not None:
        root_cause.why_5 = rc_data.why_5
    if rc_data.fishbone_category is not None:
        root_cause.fishbone_category = rc_data.fishbone_category
    if rc_data.root_cause_description is not None:
        root_cause.root_cause_description = rc_data.root_cause_description
    if rc_data.contributing_factors is not None:
        root_cause.contributing_factors = json.dumps(rc_data.contributing_factors)
    if rc_data.evidence_collected is not None:
        root_cause.evidence_collected = json.dumps(rc_data.evidence_collected)
    if rc_data.verified is not None:
        root_cause.verified = rc_data.verified
    if rc_data.verified_by is not None:
        root_cause.verified_by = rc_data.verified_by
    if rc_data.verified_at is not None:
        root_cause.verified_at = rc_data.verified_at
    
    db.commit()
    db.refresh(root_cause)
    
    return {
        'id': root_cause.id,
        'ocap_id': root_cause.ocap_id,
        'analysis_method': root_cause.analysis_method,
        'why_1': root_cause.why_1,
        'why_2': root_cause.why_2,
        'why_3': root_cause.why_3,
        'why_4': root_cause.why_4,
        'why_5': root_cause.why_5,
        'fishbone_category': root_cause.fishbone_category,
        'root_cause_description': root_cause.root_cause_description,
        'contributing_factors': root_cause.get_contributing_factors() if hasattr(root_cause, 'get_contributing_factors') else [],
        'evidence_collected': root_cause.get_evidence_collected() if hasattr(root_cause, 'get_evidence_collected') else {},
        'verified': root_cause.verified,
        'verified_by': root_cause.verified_by,
        'verified_at': root_cause.verified_at,
        'created_at': root_cause.created_at,
        'updated_at': root_cause.updated_at
    }


@router.delete("/ocaps/{ocap_id}/root-causes/{rc_id}")
async def delete_ocap_root_cause(ocap_id: int, rc_id: int, db: Session = Depends(get_db)):
    ocap = db.query(OCAP).filter(OCAP.id == ocap_id).first()
    if not ocap:
        raise HTTPException(status_code=404, detail="OCAP不存在")
    
    root_cause = db.query(OCAPRootCause).filter(
        OCAPRootCause.id == rc_id,
        OCAPRootCause.ocap_id == ocap_id
    ).first()
    if not root_cause:
        raise HTTPException(status_code=404, detail="根本原因分析不存在")
    
    db.delete(root_cause)
    db.commit()
    
    return {"message": "根本原因分析删除成功"}


# ==================== OCAP Corrective Action API ====================

@router.get("/ocaps/{ocap_id}/corrective-actions", response_model=List[OCAPCorrectiveActionResponse])
async def get_ocap_corrective_actions(ocap_id: int, db: Session = Depends(get_db)):
    ocap = db.query(OCAP).filter(OCAP.id == ocap_id).first()
    if not ocap:
        raise HTTPException(status_code=404, detail="OCAP不存在")
    
    corrective_actions = db.query(OCAPCorrectiveAction).filter(OCAPCorrectiveAction.ocap_id == ocap_id).all()
    
    return [
        {
            'id': ca.id,
            'ocap_id': ca.ocap_id,
            'root_cause_id': ca.root_cause_id,
            'action_description': ca.action_description,
            'action_type': ca.action_type,
            'responsible_person': ca.responsible_person,
            'target_date': ca.target_date,
            'actual_date': ca.actual_date,
            'effectiveness_verified': ca.effectiveness_verified,
            'verification_method': ca.verification_method,
            'verification_result': ca.verification_result,
            'status': ca.status,
            'created_at': ca.created_at,
            'updated_at': ca.updated_at
        }
        for ca in corrective_actions
    ]


@router.post("/ocaps/{ocap_id}/corrective-actions", response_model=OCAPCorrectiveActionResponse)
async def create_ocap_corrective_action(ocap_id: int, ca_data: OCAPCorrectiveActionCreate, db: Session = Depends(get_db)):
    ocap = db.query(OCAP).filter(OCAP.id == ocap_id).first()
    if not ocap:
        raise HTTPException(status_code=404, detail="OCAP不存在")
    
    if ca_data.root_cause_id:
        root_cause = db.query(OCAPRootCause).filter(OCAPRootCause.id == ca_data.root_cause_id).first()
        if not root_cause:
            raise HTTPException(status_code=404, detail="根本原因分析不存在")
    
    new_corrective_action = OCAPCorrectiveAction(
        ocap_id=ocap_id,
        root_cause_id=ca_data.root_cause_id,
        action_description=ca_data.action_description,
        action_type=ca_data.action_type.value if ca_data.action_type else "permanent",
        responsible_person=ca_data.responsible_person,
        target_date=ca_data.target_date,
        actual_date=ca_data.actual_date,
        effectiveness_verified=ca_data.effectiveness_verified,
        verification_method=ca_data.verification_method,
        verification_result=ca_data.verification_result,
        status=ca_data.status.value if ca_data.status else "planned"
    )
    db.add(new_corrective_action)
    db.commit()
    db.refresh(new_corrective_action)
    
    return {
        'id': new_corrective_action.id,
        'ocap_id': new_corrective_action.ocap_id,
        'root_cause_id': new_corrective_action.root_cause_id,
        'action_description': new_corrective_action.action_description,
        'action_type': new_corrective_action.action_type,
        'responsible_person': new_corrective_action.responsible_person,
        'target_date': new_corrective_action.target_date,
        'actual_date': new_corrective_action.actual_date,
        'effectiveness_verified': new_corrective_action.effectiveness_verified,
        'verification_method': new_corrective_action.verification_method,
        'verification_result': new_corrective_action.verification_result,
        'status': new_corrective_action.status,
        'created_at': new_corrective_action.created_at,
        'updated_at': new_corrective_action.updated_at
    }


@router.put("/ocaps/{ocap_id}/corrective-actions/{ca_id}", response_model=OCAPCorrectiveActionResponse)
async def update_ocap_corrective_action(ocap_id: int, ca_id: int, ca_data: OCAPCorrectiveActionUpdate, db: Session = Depends(get_db)):
    ocap = db.query(OCAP).filter(OCAP.id == ocap_id).first()
    if not ocap:
        raise HTTPException(status_code=404, detail="OCAP不存在")
    
    corrective_action = db.query(OCAPCorrectiveAction).filter(
        OCAPCorrectiveAction.id == ca_id,
        OCAPCorrectiveAction.ocap_id == ocap_id
    ).first()
    if not corrective_action:
        raise HTTPException(status_code=404, detail="纠正措施不存在")
    
    if ca_data.root_cause_id is not None:
        corrective_action.root_cause_id = ca_data.root_cause_id
    if ca_data.action_description is not None:
        corrective_action.action_description = ca_data.action_description
    if ca_data.action_type is not None:
        corrective_action.action_type = ca_data.action_type.value
    if ca_data.responsible_person is not None:
        corrective_action.responsible_person = ca_data.responsible_person
    if ca_data.target_date is not None:
        corrective_action.target_date = ca_data.target_date
    if ca_data.actual_date is not None:
        corrective_action.actual_date = ca_data.actual_date
    if ca_data.effectiveness_verified is not None:
        corrective_action.effectiveness_verified = ca_data.effectiveness_verified
    if ca_data.verification_method is not None:
        corrective_action.verification_method = ca_data.verification_method
    if ca_data.verification_result is not None:
        corrective_action.verification_result = ca_data.verification_result
    if ca_data.status is not None:
        corrective_action.status = ca_data.status.value
    
    db.commit()
    db.refresh(corrective_action)
    
    return {
        'id': corrective_action.id,
        'ocap_id': corrective_action.ocap_id,
        'root_cause_id': corrective_action.root_cause_id,
        'action_description': corrective_action.action_description,
        'action_type': corrective_action.action_type,
        'responsible_person': corrective_action.responsible_person,
        'target_date': corrective_action.target_date,
        'actual_date': corrective_action.actual_date,
        'effectiveness_verified': corrective_action.effectiveness_verified,
        'verification_method': corrective_action.verification_method,
        'verification_result': corrective_action.verification_result,
        'status': corrective_action.status,
        'created_at': corrective_action.created_at,
        'updated_at': corrective_action.updated_at
    }


@router.delete("/ocaps/{ocap_id}/corrective-actions/{ca_id}")
async def delete_ocap_corrective_action(ocap_id: int, ca_id: int, db: Session = Depends(get_db)):
    ocap = db.query(OCAP).filter(OCAP.id == ocap_id).first()
    if not ocap:
        raise HTTPException(status_code=404, detail="OCAP不存在")
    
    corrective_action = db.query(OCAPCorrectiveAction).filter(
        OCAPCorrectiveAction.id == ca_id,
        OCAPCorrectiveAction.ocap_id == ocap_id
    ).first()
    if not corrective_action:
        raise HTTPException(status_code=404, detail="纠正措施不存在")
    
    db.delete(corrective_action)
    db.commit()
    
    return {"message": "纠正措施删除成功"}


# ==================== MSA Study API ====================

def build_msa_study_response(study: MSAStudy, db: Session) -> dict:
    parts = db.query(MSAPart).filter(MSAPart.msa_study_id == study.id).order_by(MSAPart.sort_order).all()
    operators = db.query(MSAOperator).filter(MSAOperator.msa_study_id == study.id).order_by(MSAOperator.sort_order).all()
    measurements = db.query(MSAMeasurement).filter(MSAMeasurement.msa_study_id == study.id).all()
    result = db.query(MSAResult).filter(MSAResult.msa_study_id == study.id).first()
    
    return {
        'id': study.id,
        'line_id': study.line_id,
        'study_name': study.study_name,
        'study_type': study.study_type,
        'status': study.status,
        'measurement_system': study.measurement_system,
        'characteristic': study.characteristic,
        'specification_lower': study.specification_lower,
        'specification_upper': study.specification_upper,
        'specification_target': study.specification_target,
        'tolerance': study.tolerance,
        'number_of_parts': study.number_of_parts,
        'number_of_operators': study.number_of_operators,
        'number_of_replicates': study.number_of_replicates,
        'random_order': study.random_order,
        'created_by': study.created_by,
        'created_at': study.created_at,
        'updated_at': study.updated_at,
        'parts': [
            {
                'id': p.id,
                'msa_study_id': p.msa_study_id,
                'part_number': p.part_number,
                'part_name': p.part_name,
                'reference_value': p.reference_value,
                'sort_order': p.sort_order
            }
            for p in parts
        ],
        'operators': [
            {
                'id': o.id,
                'msa_study_id': o.msa_study_id,
                'operator_name': o.operator_name,
                'operator_id': o.operator_id,
                'sort_order': o.sort_order
            }
            for o in operators
        ],
        'measurements': [
            {
                'id': m.id,
                'msa_study_id': m.msa_study_id,
                'part_id': m.part_id,
                'operator_id': m.operator_id,
                'replicate': m.replicate,
                'measurement_value': m.measurement_value,
                'measurement_order': m.measurement_order,
                'measured_at': m.measured_at
            }
            for m in measurements
        ],
        'result': {
            'id': result.id,
            'msa_study_id': result.msa_study_id,
            'study_type': result.study_type,
            'calculation_method': result.calculation_method,
            'variance_repeatability': result.variance_repeatability,
            'variance_reproducibility': result.variance_reproducibility,
            'variance_grr': result.variance_grr,
            'variance_part': result.variance_part,
            'variance_total': result.variance_total,
            'stddev_repeatability': result.stddev_repeatability,
            'stddev_reproducibility': result.stddev_reproducibility,
            'stddev_grr': result.stddev_grr,
            'stddev_part': result.stddev_part,
            'stddev_total': result.stddev_total,
            'percent_grr': result.percent_grr,
            'percent_tolerance': result.percent_tolerance,
            'ndc': result.ndc,
            'grr_acceptance': result.grr_acceptance,
            'ndc_acceptance': result.ndc_acceptance,
            'overall_acceptance': result.overall_acceptance,
            'detailed_results': result.get_detailed_results(),
            'calculated_at': result.calculated_at,
            'created_at': result.created_at
        } if result else None
    }


@router.post("/msa-studies", response_model=MSAStudyResponse)
async def create_msa_study(study_data: MSAStudyCreate, db: Session = Depends(get_db)):
    if study_data.line_id:
        line = db.query(ProductionLine).filter(ProductionLine.id == study_data.line_id).first()
        if not line:
            raise HTTPException(status_code=404, detail="产线不存在")
    
    new_study = MSAStudy(
        line_id=study_data.line_id,
        study_name=study_data.study_name,
        study_type=study_data.study_type.value if study_data.study_type else "grr",
        status=study_data.status.value if study_data.status else "draft",
        measurement_system=study_data.measurement_system,
        characteristic=study_data.characteristic,
        specification_lower=study_data.specification_lower,
        specification_upper=study_data.specification_upper,
        specification_target=study_data.specification_target,
        tolerance=study_data.tolerance,
        number_of_parts=study_data.number_of_parts,
        number_of_operators=study_data.number_of_operators,
        number_of_replicates=study_data.number_of_replicates,
        random_order=study_data.random_order,
        created_by=study_data.created_by
    )
    db.add(new_study)
    db.commit()
    db.refresh(new_study)
    
    if study_data.parts:
        for idx, part_data in enumerate(study_data.parts):
            new_part = MSAPart(
                msa_study_id=new_study.id,
                part_number=part_data.part_number,
                part_name=part_data.part_name,
                reference_value=part_data.reference_value,
                sort_order=part_data.sort_order if part_data.sort_order else idx
            )
            db.add(new_part)
    
    if study_data.operators:
        for idx, op_data in enumerate(study_data.operators):
            new_operator = MSAOperator(
                msa_study_id=new_study.id,
                operator_name=op_data.operator_name,
                operator_id=op_data.operator_id,
                sort_order=op_data.sort_order if op_data.sort_order else idx
            )
            db.add(new_operator)
    
    if study_data.measurements:
        for meas_data in study_data.measurements:
            new_measurement = MSAMeasurement(
                msa_study_id=new_study.id,
                part_id=meas_data.part_id,
                operator_id=meas_data.operator_id,
                replicate=meas_data.replicate,
                measurement_value=meas_data.measurement_value,
                measurement_order=meas_data.measurement_order,
                measured_at=meas_data.measured_at
            )
            db.add(new_measurement)
    
    db.commit()
    
    return build_msa_study_response(new_study, db)


@router.get("/msa-studies", response_model=List[MSAStudyResponse])
async def get_msa_studies(
    line_id: Optional[int] = None,
    study_type: Optional[str] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(MSAStudy)
    if line_id:
        query = query.filter(MSAStudy.line_id == line_id)
    if study_type:
        query = query.filter(MSAStudy.study_type == study_type)
    if status:
        query = query.filter(MSAStudy.status == status)
    
    studies = query.order_by(MSAStudy.created_at.desc()).all()
    
    return [build_msa_study_response(study, db) for study in studies]


@router.get("/msa-studies/{study_id}", response_model=MSAStudyResponse)
async def get_msa_study(study_id: int, db: Session = Depends(get_db)):
    study = db.query(MSAStudy).filter(MSAStudy.id == study_id).first()
    if not study:
        raise HTTPException(status_code=404, detail="MSA研究不存在")
    
    return build_msa_study_response(study, db)


@router.put("/msa-studies/{study_id}", response_model=MSAStudyResponse)
async def update_msa_study(study_id: int, study_data: MSAStudyUpdate, db: Session = Depends(get_db)):
    study = db.query(MSAStudy).filter(MSAStudy.id == study_id).first()
    if not study:
        raise HTTPException(status_code=404, detail="MSA研究不存在")
    
    if study_data.study_name is not None:
        study.study_name = study_data.study_name
    if study_data.study_type is not None:
        study.study_type = study_data.study_type.value
    if study_data.status is not None:
        study.status = study_data.status.value
    if study_data.measurement_system is not None:
        study.measurement_system = study_data.measurement_system
    if study_data.characteristic is not None:
        study.characteristic = study_data.characteristic
    if study_data.specification_lower is not None:
        study.specification_lower = study_data.specification_lower
    if study_data.specification_upper is not None:
        study.specification_upper = study_data.specification_upper
    if study_data.specification_target is not None:
        study.specification_target = study_data.specification_target
    if study_data.tolerance is not None:
        study.tolerance = study_data.tolerance
    if study_data.number_of_parts is not None:
        study.number_of_parts = study_data.number_of_parts
    if study_data.number_of_operators is not None:
        study.number_of_operators = study_data.number_of_operators
    if study_data.number_of_replicates is not None:
        study.number_of_replicates = study_data.number_of_replicates
    if study_data.random_order is not None:
        study.random_order = study_data.random_order
    
    db.commit()
    db.refresh(study)
    
    return build_msa_study_response(study, db)


@router.delete("/msa-studies/{study_id}")
async def delete_msa_study(study_id: int, db: Session = Depends(get_db)):
    study = db.query(MSAStudy).filter(MSAStudy.id == study_id).first()
    if not study:
        raise HTTPException(status_code=404, detail="MSA研究不存在")
    
    db.query(MSAMeasurement).filter(MSAMeasurement.msa_study_id == study_id).delete()
    db.query(MSAPart).filter(MSAPart.msa_study_id == study_id).delete()
    db.query(MSAOperator).filter(MSAOperator.msa_study_id == study_id).delete()
    db.query(MSAResult).filter(MSAResult.msa_study_id == study_id).delete()
    
    db.delete(study)
    db.commit()
    
    return {"message": "MSA研究删除成功"}


@router.get("/production-lines/{line_id}/msa-studies", response_model=List[MSAStudyResponse])
async def get_line_msa_studies(line_id: int, db: Session = Depends(get_db)):
    line = db.query(ProductionLine).filter(ProductionLine.id == line_id).first()
    if not line:
        raise HTTPException(status_code=404, detail="产线不存在")
    
    studies = db.query(MSAStudy).filter(
        MSAStudy.line_id == line_id
    ).order_by(MSAStudy.created_at.desc()).all()
    
    return [build_msa_study_response(study, db) for study in studies]


# ==================== MSA Part API ====================

@router.get("/msa-studies/{study_id}/parts", response_model=List[MSAPartResponse])
async def get_msa_parts(study_id: int, db: Session = Depends(get_db)):
    study = db.query(MSAStudy).filter(MSAStudy.id == study_id).first()
    if not study:
        raise HTTPException(status_code=404, detail="MSA研究不存在")
    
    parts = db.query(MSAPart).filter(MSAPart.msa_study_id == study_id).order_by(MSAPart.sort_order).all()
    
    return [
        {
            'id': p.id,
            'msa_study_id': p.msa_study_id,
            'part_number': p.part_number,
            'part_name': p.part_name,
            'reference_value': p.reference_value,
            'sort_order': p.sort_order
        }
        for p in parts
    ]


@router.post("/msa-studies/{study_id}/parts", response_model=MSAPartResponse)
async def create_msa_part(study_id: int, part_data: MSAPartCreate, db: Session = Depends(get_db)):
    study = db.query(MSAStudy).filter(MSAStudy.id == study_id).first()
    if not study:
        raise HTTPException(status_code=404, detail="MSA研究不存在")
    
    new_part = MSAPart(
        msa_study_id=study_id,
        part_number=part_data.part_number,
        part_name=part_data.part_name,
        reference_value=part_data.reference_value,
        sort_order=part_data.sort_order
    )
    db.add(new_part)
    db.commit()
    db.refresh(new_part)
    
    return {
        'id': new_part.id,
        'msa_study_id': new_part.msa_study_id,
        'part_number': new_part.part_number,
        'part_name': new_part.part_name,
        'reference_value': new_part.reference_value,
        'sort_order': new_part.sort_order
    }


@router.put("/msa-studies/{study_id}/parts/{part_id}", response_model=MSAPartResponse)
async def update_msa_part(study_id: int, part_id: int, part_data: MSAPartUpdate, db: Session = Depends(get_db)):
    study = db.query(MSAStudy).filter(MSAStudy.id == study_id).first()
    if not study:
        raise HTTPException(status_code=404, detail="MSA研究不存在")
    
    part = db.query(MSAPart).filter(
        MSAPart.id == part_id,
        MSAPart.msa_study_id == study_id
    ).first()
    if not part:
        raise HTTPException(status_code=404, detail="MSA零件不存在")
    
    if part_data.part_number is not None:
        part.part_number = part_data.part_number
    if part_data.part_name is not None:
        part.part_name = part_data.part_name
    if part_data.reference_value is not None:
        part.reference_value = part_data.reference_value
    if part_data.sort_order is not None:
        part.sort_order = part_data.sort_order
    
    db.commit()
    db.refresh(part)
    
    return {
        'id': part.id,
        'msa_study_id': part.msa_study_id,
        'part_number': part.part_number,
        'part_name': part.part_name,
        'reference_value': part.reference_value,
        'sort_order': part.sort_order
    }


@router.delete("/msa-studies/{study_id}/parts/{part_id}")
async def delete_msa_part(study_id: int, part_id: int, db: Session = Depends(get_db)):
    study = db.query(MSAStudy).filter(MSAStudy.id == study_id).first()
    if not study:
        raise HTTPException(status_code=404, detail="MSA研究不存在")
    
    part = db.query(MSAPart).filter(
        MSAPart.id == part_id,
        MSAPart.msa_study_id == study_id
    ).first()
    if not part:
        raise HTTPException(status_code=404, detail="MSA零件不存在")
    
    db.query(MSAMeasurement).filter(MSAMeasurement.part_id == part_id).delete()
    
    db.delete(part)
    db.commit()
    
    return {"message": "MSA零件删除成功"}


# ==================== MSA Operator API ====================

@router.get("/msa-studies/{study_id}/operators", response_model=List[MSAOperatorResponse])
async def get_msa_operators(study_id: int, db: Session = Depends(get_db)):
    study = db.query(MSAStudy).filter(MSAStudy.id == study_id).first()
    if not study:
        raise HTTPException(status_code=404, detail="MSA研究不存在")
    
    operators = db.query(MSAOperator).filter(MSAOperator.msa_study_id == study_id).order_by(MSAOperator.sort_order).all()
    
    return [
        {
            'id': o.id,
            'msa_study_id': o.msa_study_id,
            'operator_name': o.operator_name,
            'operator_id': o.operator_id,
            'sort_order': o.sort_order
        }
        for o in operators
    ]


@router.post("/msa-studies/{study_id}/operators", response_model=MSAOperatorResponse)
async def create_msa_operator(study_id: int, op_data: MSAOperatorCreate, db: Session = Depends(get_db)):
    study = db.query(MSAStudy).filter(MSAStudy.id == study_id).first()
    if not study:
        raise HTTPException(status_code=404, detail="MSA研究不存在")
    
    new_operator = MSAOperator(
        msa_study_id=study_id,
        operator_name=op_data.operator_name,
        operator_id=op_data.operator_id,
        sort_order=op_data.sort_order
    )
    db.add(new_operator)
    db.commit()
    db.refresh(new_operator)
    
    return {
        'id': new_operator.id,
        'msa_study_id': new_operator.msa_study_id,
        'operator_name': new_operator.operator_name,
        'operator_id': new_operator.operator_id,
        'sort_order': new_operator.sort_order
    }


@router.put("/msa-studies/{study_id}/operators/{operator_id}", response_model=MSAOperatorResponse)
async def update_msa_operator(study_id: int, operator_id: int, op_data: MSAOperatorUpdate, db: Session = Depends(get_db)):
    study = db.query(MSAStudy).filter(MSAStudy.id == study_id).first()
    if not study:
        raise HTTPException(status_code=404, detail="MSA研究不存在")
    
    operator = db.query(MSAOperator).filter(
        MSAOperator.id == operator_id,
        MSAOperator.msa_study_id == study_id
    ).first()
    if not operator:
        raise HTTPException(status_code=404, detail="MSA操作员不存在")
    
    if op_data.operator_name is not None:
        operator.operator_name = op_data.operator_name
    if op_data.operator_id is not None:
        operator.operator_id = op_data.operator_id
    if op_data.sort_order is not None:
        operator.sort_order = op_data.sort_order
    
    db.commit()
    db.refresh(operator)
    
    return {
        'id': operator.id,
        'msa_study_id': operator.msa_study_id,
        'operator_name': operator.operator_name,
        'operator_id': operator.operator_id,
        'sort_order': operator.sort_order
    }


@router.delete("/msa-studies/{study_id}/operators/{operator_id}")
async def delete_msa_operator(study_id: int, operator_id: int, db: Session = Depends(get_db)):
    study = db.query(MSAStudy).filter(MSAStudy.id == study_id).first()
    if not study:
        raise HTTPException(status_code=404, detail="MSA研究不存在")
    
    operator = db.query(MSAOperator).filter(
        MSAOperator.id == operator_id,
        MSAOperator.msa_study_id == study_id
    ).first()
    if not operator:
        raise HTTPException(status_code=404, detail="MSA操作员不存在")
    
    db.query(MSAMeasurement).filter(MSAMeasurement.operator_id == operator_id).delete()
    
    db.delete(operator)
    db.commit()
    
    return {"message": "MSA操作员删除成功"}


# ==================== MSA Measurement API ====================

@router.get("/msa-studies/{study_id}/measurements", response_model=List[MSAMeasurementResponse])
async def get_msa_measurements(study_id: int, db: Session = Depends(get_db)):
    study = db.query(MSAStudy).filter(MSAStudy.id == study_id).first()
    if not study:
        raise HTTPException(status_code=404, detail="MSA研究不存在")
    
    measurements = db.query(MSAMeasurement).filter(MSAMeasurement.msa_study_id == study_id).all()
    
    return [
        {
            'id': m.id,
            'msa_study_id': m.msa_study_id,
            'part_id': m.part_id,
            'operator_id': m.operator_id,
            'replicate': m.replicate,
            'measurement_value': m.measurement_value,
            'measurement_order': m.measurement_order,
            'measured_at': m.measured_at
        }
        for m in measurements
    ]


@router.post("/msa-studies/{study_id}/measurements", response_model=MSAMeasurementResponse)
async def create_msa_measurement(study_id: int, meas_data: MSAMeasurementCreate, db: Session = Depends(get_db)):
    study = db.query(MSAStudy).filter(MSAStudy.id == study_id).first()
    if not study:
        raise HTTPException(status_code=404, detail="MSA研究不存在")
    
    part = db.query(MSAPart).filter(MSAPart.id == meas_data.part_id).first()
    if not part:
        raise HTTPException(status_code=404, detail="MSA零件不存在")
    
    operator = db.query(MSAOperator).filter(MSAOperator.id == meas_data.operator_id).first()
    if not operator:
        raise HTTPException(status_code=404, detail="MSA操作员不存在")
    
    new_measurement = MSAMeasurement(
        msa_study_id=study_id,
        part_id=meas_data.part_id,
        operator_id=meas_data.operator_id,
        replicate=meas_data.replicate,
        measurement_value=meas_data.measurement_value,
        measurement_order=meas_data.measurement_order,
        measured_at=meas_data.measured_at
    )
    db.add(new_measurement)
    db.commit()
    db.refresh(new_measurement)
    
    return {
        'id': new_measurement.id,
        'msa_study_id': new_measurement.msa_study_id,
        'part_id': new_measurement.part_id,
        'operator_id': new_measurement.operator_id,
        'replicate': new_measurement.replicate,
        'measurement_value': new_measurement.measurement_value,
        'measurement_order': new_measurement.measurement_order,
        'measured_at': new_measurement.measured_at
    }


@router.put("/msa-studies/{study_id}/measurements/{meas_id}", response_model=MSAMeasurementResponse)
async def update_msa_measurement(study_id: int, meas_id: int, meas_data: MSAMeasurementUpdate, db: Session = Depends(get_db)):
    study = db.query(MSAStudy).filter(MSAStudy.id == study_id).first()
    if not study:
        raise HTTPException(status_code=404, detail="MSA研究不存在")
    
    measurement = db.query(MSAMeasurement).filter(
        MSAMeasurement.id == meas_id,
        MSAMeasurement.msa_study_id == study_id
    ).first()
    if not measurement:
        raise HTTPException(status_code=404, detail="MSA测量数据不存在")
    
    if meas_data.part_id is not None:
        measurement.part_id = meas_data.part_id
    if meas_data.operator_id is not None:
        measurement.operator_id = meas_data.operator_id
    if meas_data.replicate is not None:
        measurement.replicate = meas_data.replicate
    if meas_data.measurement_value is not None:
        measurement.measurement_value = meas_data.measurement_value
    if meas_data.measurement_order is not None:
        measurement.measurement_order = meas_data.measurement_order
    if meas_data.measured_at is not None:
        measurement.measured_at = meas_data.measured_at
    
    db.commit()
    db.refresh(measurement)
    
    return {
        'id': measurement.id,
        'msa_study_id': measurement.msa_study_id,
        'part_id': measurement.part_id,
        'operator_id': measurement.operator_id,
        'replicate': measurement.replicate,
        'measurement_value': measurement.measurement_value,
        'measurement_order': measurement.measurement_order,
        'measured_at': measurement.measured_at
    }


@router.delete("/msa-studies/{study_id}/measurements/{meas_id}")
async def delete_msa_measurement(study_id: int, meas_id: int, db: Session = Depends(get_db)):
    study = db.query(MSAStudy).filter(MSAStudy.id == study_id).first()
    if not study:
        raise HTTPException(status_code=404, detail="MSA研究不存在")
    
    measurement = db.query(MSAMeasurement).filter(
        MSAMeasurement.id == meas_id,
        MSAMeasurement.msa_study_id == study_id
    ).first()
    if not measurement:
        raise HTTPException(status_code=404, detail="MSA测量数据不存在")
    
    db.delete(measurement)
    db.commit()
    
    return {"message": "MSA测量数据删除成功"}


# ==================== MSA Result API ====================

def build_msa_study_response(study: MSAStudy, db: Session) -> dict:
    from ..services.msa_service import calculate_grr_xr
    
    parts = db.query(MSAPart).filter(MSAPart.msa_study_id == study.id).order_by(MSAPart.sort_order).all()
    operators = db.query(MSAOperator).filter(MSAOperator.msa_study_id == study.id).order_by(MSAOperator.sort_order).all()
    measurements = db.query(MSAMeasurement).filter(MSAMeasurement.msa_study_id == study.id).all()
    result = db.query(MSAResult).filter(MSAResult.msa_study_id == study.id).first()
    
    return {
        'id': study.id,
        'line_id': study.line_id,
        'study_name': study.study_name,
        'study_type': study.study_type,
        'status': study.status,
        'measurement_system': study.measurement_system,
        'characteristic': study.characteristic,
        'specification_lower': study.specification_lower,
        'specification_upper': study.specification_upper,
        'specification_target': study.specification_target,
        'tolerance': study.tolerance,
        'number_of_parts': study.number_of_parts,
        'number_of_operators': study.number_of_operators,
        'number_of_replicates': study.number_of_replicates,
        'random_order': study.random_order,
        'created_by': study.created_by,
        'created_at': study.created_at,
        'updated_at': study.updated_at,
        'parts': [
            {
                'id': p.id,
                'msa_study_id': p.msa_study_id,
                'part_number': p.part_number,
                'part_name': p.part_name,
                'reference_value': p.reference_value,
                'sort_order': p.sort_order
            }
            for p in parts
        ],
        'operators': [
            {
                'id': o.id,
                'msa_study_id': o.msa_study_id,
                'operator_name': o.operator_name,
                'operator_id': o.operator_id,
                'sort_order': o.sort_order
            }
            for o in operators
        ],
        'measurements': [
            {
                'id': m.id,
                'msa_study_id': m.msa_study_id,
                'part_id': m.part_id,
                'operator_id': m.operator_id,
                'replicate': m.replicate,
                'measurement_value': m.measurement_value,
                'measurement_order': m.measurement_order,
                'measured_at': m.measured_at
            }
            for m in measurements
        ],
        'result': {
            'id': result.id,
            'msa_study_id': result.msa_study_id,
            'study_type': result.study_type,
            'calculation_method': result.calculation_method,
            'variance_repeatability': result.variance_repeatability,
            'variance_reproducibility': result.variance_reproducibility,
            'variance_grr': result.variance_grr,
            'variance_part': result.variance_part,
            'variance_total': result.variance_total,
            'stddev_repeatability': result.stddev_repeatability,
            'stddev_reproducibility': result.stddev_reproducibility,
            'stddev_grr': result.stddev_grr,
            'stddev_part': result.stddev_part,
            'stddev_total': result.stddev_total,
            'percent_grr': result.percent_grr,
            'percent_tolerance': result.percent_tolerance,
            'ndc': result.ndc,
            'grr_acceptance': result.grr_acceptance,
            'ndc_acceptance': result.ndc_acceptance,
            'overall_acceptance': result.overall_acceptance,
            'detailed_results': result.get_detailed_results(),
            'calculated_at': result.calculated_at,
            'created_at': result.created_at
        } if result else None
    }


@router.get("/msa-studies/{study_id}/result", response_model=MSAResultResponse)
async def get_msa_result(study_id: int, db: Session = Depends(get_db)):
    study = db.query(MSAStudy).filter(MSAStudy.id == study_id).first()
    if not study:
        raise HTTPException(status_code=404, detail="MSA研究不存在")
    
    result = db.query(MSAResult).filter(MSAResult.msa_study_id == study_id).first()
    if not result:
        raise HTTPException(status_code=404, detail="MSA结果不存在")
    
    return {
        'id': result.id,
        'msa_study_id': result.msa_study_id,
        'study_type': result.study_type,
        'calculation_method': result.calculation_method,
        'variance_repeatability': result.variance_repeatability,
        'variance_reproducibility': result.variance_reproducibility,
        'variance_grr': result.variance_grr,
        'variance_part': result.variance_part,
        'variance_total': result.variance_total,
        'stddev_repeatability': result.stddev_repeatability,
        'stddev_reproducibility': result.stddev_reproducibility,
        'stddev_grr': result.stddev_grr,
        'stddev_part': result.stddev_part,
        'stddev_total': result.stddev_total,
        'percent_grr': result.percent_grr,
        'percent_tolerance': result.percent_tolerance,
        'ndc': result.ndc,
        'grr_acceptance': result.grr_acceptance,
        'ndc_acceptance': result.ndc_acceptance,
        'overall_acceptance': result.overall_acceptance,
        'detailed_results': result.get_detailed_results(),
        'calculated_at': result.calculated_at,
        'created_at': result.created_at
    }


@router.post("/msa-studies/{study_id}/calculate")
async def calculate_msa(study_id: int, calculation_method: str = "xr", db: Session = Depends(get_db)):
    from ..services.msa_service import calculate_grr_xr, calculate_grr_anova
    
    study = db.query(MSAStudy).filter(MSAStudy.id == study_id).first()
    if not study:
        raise HTTPException(status_code=404, detail="MSA研究不存在")
    
    parts = db.query(MSAPart).filter(MSAPart.msa_study_id == study_id).all()
    operators = db.query(MSAOperator).filter(MSAOperator.msa_study_id == study_id).all()
    measurements = db.query(MSAMeasurement).filter(MSAMeasurement.msa_study_id == study_id).all()
    
    if not parts or not operators or not measurements:
        raise HTTPException(status_code=400, detail="数据不足：需要零件、操作员和测量数据")
    
    study_data = {
        'parts': [{'id': p.id, 'part_number': p.part_number, 'part_name': p.part_name} for p in parts],
        'operators': [{'id': o.id, 'operator_name': o.operator_name, 'operator_id': o.operator_id} for o in operators],
        'measurements': [
            {
                'part_id': m.part_id,
                'operator_id': m.operator_id,
                'replicate': m.replicate,
                'measurement_value': m.measurement_value
            }
            for m in measurements
        ],
        'tolerance': study.tolerance
    }
    
    if study.study_type == 'grr':
        if calculation_method == 'anova':
            calc_result = calculate_grr_anova(study_data)
        else:
            calc_result = calculate_grr_xr(study_data)
    else:
        raise HTTPException(status_code=400, detail=f"不支持的研究类型: {study.study_type}")
    
    if not calc_result.get('valid', False):
        return calc_result
    
    existing_result = db.query(MSAResult).filter(MSAResult.msa_study_id == study_id).first()
    
    if existing_result:
        existing_result.study_type = calc_result.get('study_type', 'grr')
        existing_result.calculation_method = calc_result.get('calculation_method', 'xr')
        existing_result.variance_repeatability = calc_result.get('variance_repeatability')
        existing_result.variance_reproducibility = calc_result.get('variance_reproducibility')
        existing_result.variance_grr = calc_result.get('variance_grr')
        existing_result.variance_part = calc_result.get('variance_part')
        existing_result.variance_total = calc_result.get('variance_total')
        existing_result.stddev_repeatability = calc_result.get('stddev_repeatability')
        existing_result.stddev_reproducibility = calc_result.get('stddev_reproducibility')
        existing_result.stddev_grr = calc_result.get('stddev_grr')
        existing_result.stddev_part = calc_result.get('stddev_part')
        existing_result.stddev_total = calc_result.get('stddev_total')
        existing_result.percent_grr = calc_result.get('percent_grr')
        existing_result.percent_tolerance = calc_result.get('percent_tolerance')
        existing_result.ndc = calc_result.get('ndc')
        existing_result.grr_acceptance = calc_result.get('grr_acceptance')
        existing_result.ndc_acceptance = calc_result.get('ndc_acceptance')
        existing_result.overall_acceptance = calc_result.get('overall_acceptance')
        existing_result.detailed_results = json.dumps(calc_result.get('detailed_results', {}))
        existing_result.calculated_at = datetime.now()
        
        result_obj = existing_result
    else:
        new_result = MSAResult(
            msa_study_id=study_id,
            study_type=calc_result.get('study_type', 'grr'),
            calculation_method=calc_result.get('calculation_method', 'xr'),
            variance_repeatability=calc_result.get('variance_repeatability'),
            variance_reproducibility=calc_result.get('variance_reproducibility'),
            variance_grr=calc_result.get('variance_grr'),
            variance_part=calc_result.get('variance_part'),
            variance_total=calc_result.get('variance_total'),
            stddev_repeatability=calc_result.get('stddev_repeatability'),
            stddev_reproducibility=calc_result.get('stddev_reproducibility'),
            stddev_grr=calc_result.get('stddev_grr'),
            stddev_part=calc_result.get('stddev_part'),
            stddev_total=calc_result.get('stddev_total'),
            percent_grr=calc_result.get('percent_grr'),
            percent_tolerance=calc_result.get('percent_tolerance'),
            ndc=calc_result.get('ndc'),
            grr_acceptance=calc_result.get('grr_acceptance'),
            ndc_acceptance=calc_result.get('ndc_acceptance'),
            overall_acceptance=calc_result.get('overall_acceptance'),
            detailed_results=json.dumps(calc_result.get('detailed_results', {})),
            calculated_at=datetime.now()
        )
        db.add(new_result)
        result_obj = new_result
    
    study.status = 'completed'
    db.commit()
    db.refresh(result_obj)
    
    return {
        'message': 'MSA计算完成',
        'result': {
            'id': result_obj.id,
            'msa_study_id': result_obj.msa_study_id,
            'study_type': result_obj.study_type,
            'calculation_method': result_obj.calculation_method,
            'variance_repeatability': result_obj.variance_repeatability,
            'variance_reproducibility': result_obj.variance_reproducibility,
            'variance_grr': result_obj.variance_grr,
            'variance_part': result_obj.variance_part,
            'variance_total': result_obj.variance_total,
            'stddev_repeatability': result_obj.stddev_repeatability,
            'stddev_reproducibility': result_obj.stddev_reproducibility,
            'stddev_grr': result_obj.stddev_grr,
            'stddev_part': result_obj.stddev_part,
            'stddev_total': result_obj.stddev_total,
            'percent_grr': result_obj.percent_grr,
            'percent_tolerance': result_obj.percent_tolerance,
            'ndc': result_obj.ndc,
            'grr_acceptance': result_obj.grr_acceptance,
            'ndc_acceptance': result_obj.ndc_acceptance,
            'overall_acceptance': result_obj.overall_acceptance,
            'detailed_results': result_obj.get_detailed_results(),
            'calculated_at': result_obj.calculated_at
        }
    }
