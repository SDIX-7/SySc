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
from ..models.models import Image, EmailSettings, User, ProductionLine, MeasurementData, AttributeData, ControlChartConfig, SamplingPlan, SamplingRecord, CapabilityAnalysis
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
    CapabilityAnalysisCreate, CapabilityAnalysisResponse
)
from ..services.detection_service import detect_image, save_json, save_detection_result_to_db, _load_model
from ..services.control_chart_service import (
    generate_control_chart_data, 
    calculate_xbar_r_chart, 
    calculate_xbar_s_chart,
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
    
    if chart_type.upper() in ['XR', 'XS']:
        measurement_data = db.query(MeasurementData).filter(
            MeasurementData.line_id == line_id
        ).order_by(MeasurementData.measurement_time.desc()).limit(250).all()
        
        if not measurement_data:
            raise HTTPException(status_code=404, detail="没有足够的量值数据")
        
        data_groups = []
        for m in measurement_data:
            values = m.get_measurement_values()
            if values:
                data_groups.append(values)
        
        if not data_groups:
            raise HTTPException(status_code=404, detail="没有有效的测量数据")
        
        if chart_type.upper() == 'XR':
            chart_data = calculate_xbar_r_chart(data_groups, subgroup_size)
        else:
            chart_data = calculate_xbar_s_chart(data_groups, subgroup_size)
        
        chart_data['line_id'] = line_id
        chart_data['line_name'] = line.line_name
        chart_data['data_type'] = line.data_type
        
        return chart_data
    
    elif chart_type.upper() in ['U', 'P', 'NP', 'C']:
        attr_data = db.query(AttributeData).filter(
            AttributeData.line_id == line_id
        ).order_by(AttributeData.inspection_time.desc()).limit(125).all()
        
        if not attr_data:
            raise HTTPException(status_code=404, detail="没有足够的属性数据")
        
        c_list = [d.defect_count for d in attr_data[::-1]]
        n_list = [float(d.sample_size) for d in attr_data[::-1]]
        
        chart_data = generate_control_chart_data(c_list, n_list)
        chart_data['chart_type'] = chart_type.upper()
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
    
    if not data.data_values or len(data.data_values) < 2:
        raise HTTPException(status_code=400, detail="数据值至少需要2个样本")
    
    validation = validate_specification_limits(data.usl, data.lsl, data.data_values)
    if not validation['valid']:
        raise HTTPException(status_code=400, detail=f"规格限验证失败: {', '.join(validation['warnings'])}")
    
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


@router.get("/capability-analysis/{analysis_id}", response_model=CapabilityAnalysisResponse)
async def get_capability_analysis(analysis_id: int, db: Session = Depends(get_db)):
    analysis = db.query(CapabilityAnalysis).filter(CapabilityAnalysis.id == analysis_id).first()
    if not analysis:
        raise HTTPException(status_code=404, detail="能力分析记录不存在")
    
    return {
        'id': analysis.id,
        'line_id': analysis.line_id,
        'analysis_name': analysis.analysis_name,
        'usl': analysis.usl,
        'lsl': analysis.lsl,
        'target': analysis.target,
        'cp': analysis.cp,
        'cpk': analysis.cpk,
        'pp': analysis.pp,
        'ppk': analysis.ppk,
        'cm': analysis.cm,
        'cmk': analysis.cmk,
        'mean': analysis.mean,
        'sigma_within': analysis.sigma_within,
        'sigma_overall': analysis.sigma_overall,
        'sigma_machine': analysis.sigma_machine,
        'sample_count': analysis.sample_count,
        'subgroup_count': analysis.subgroup_count,
        'data_values': analysis.get_data_values(),
        'status': analysis.status,
        'analysis_type': analysis.analysis_type,
        'analysis_time': analysis.analysis_time,
        'created_at': analysis.created_at
    }


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
