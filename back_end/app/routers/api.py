from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from typing import List, Optional
import os
import shutil
from datetime import datetime

from ..database import get_db
from ..models.models import Image, EmailSettings, User
from ..schemas.schemas import (
    ImageResponse, ImageCreate, DetectionResultCreate,
    EmailSettingsResponse, EmailSettingsUpdate,
    UserCreate, UserResponse,
    MessageResponse
)
from ..services.detection_service import detect_image, save_json, save_detection_result_to_db
from ..services.control_chart_service import generate_control_chart_data
from ..services.email_service import send_control_chart_alert
from ..services.auth_service import get_password_hash

router = APIRouter(prefix="/api", tags=["api"])

last_processed_max_id = 0
last_alert_time = None


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


@router.get("/images", response_model=List[ImageResponse])
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
