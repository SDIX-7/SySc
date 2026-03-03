import datetime as dt
import torch
import os
import json
import requests
from ultralytics import YOLO
import cv2

YOLO_model = None
YOLO_model_path = None

MODELS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "models")

def _load_model(model_file: str = None):
    global YOLO_model, YOLO_model_path
    
    if model_file:
        model_path = os.path.join(MODELS_DIR, model_file)
        if not os.path.exists(model_path):
            model_path = os.path.join(MODELS_DIR, "best.pt")
    else:
        model_path = os.path.join(MODELS_DIR, "best.pt")
    
    if YOLO_model is None or YOLO_model_path != model_path:
        if os.path.exists(model_path):
            YOLO_model = YOLO(model_path)
        else:
            YOLO_model = YOLO("best.pt")
        YOLO_model_path = model_path
    
    return YOLO_model


def detect_image(image_path: str, file_name: str, model_file: str = None) -> dict:
    model = _load_model(model_file)
    result = model(image_path)
    
    detection_classes = []
    detection_boxes = []
    detection_scores = []
    k = len(result[0].boxes.cls)
    
    for i in range(k):
        class_name = result[0].names[int(result[0].boxes.cls[i])].capitalize()
        detection_classes.append(class_name)
        detection_boxes.append([float(x) for x in result[0].boxes.xyxy[i].tolist()])
        score = float(result[0].boxes.conf[i])
        detection_scores.append(float(score))
    
    temp_dict = {
        "name": file_name,
        "hasDefects": k > 0,
        "captureTime": str(dt.datetime.now()),
        "detection_total_cnts": k,
        "detection_classes": detection_classes,
        "detection_boxes": detection_boxes,
        "detection_scores": detection_scores,
    }
    
    if k > 0:
        temp_dict["hasDefects"] = True
        export_dir_visuals = "./static/results/images"
        export_dir_thumbnails = "./static/results/thumbnails"
        os.makedirs(export_dir_visuals, exist_ok=True)
        os.makedirs(export_dir_thumbnails, exist_ok=True)
        
        plotted_img = result[0].plot()
        
        cv2.imwrite(os.path.join(export_dir_visuals, f"{file_name}.png"), plotted_img)
        
        thumbnail = cv2.resize(plotted_img, (200, 200), interpolation=cv2.INTER_AREA)
        cv2.imwrite(os.path.join(export_dir_thumbnails, f"{file_name}.png"), thumbnail)
    else:
        temp_dict["hasDefects"] = False
    
    return temp_dict


def save_json(data: dict, output_dir: str, filename: str):
    class NumpyEncoder(json.JSONEncoder):
        def default(self, obj):
            if isinstance(obj, (list, tuple)):
                return [float(x) if hasattr(x, '__float__') else x for x in obj]
            if hasattr(obj, '__float__'):
                return float(obj)
            return super().default(obj)
    
    file_path = os.path.join(output_dir, data["captureTime"][:10], f"{filename}.json")
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, 'w') as json_file:
        json.dump(data, json_file, cls=NumpyEncoder)


def save_detection_result_to_db(result: dict, db=None):
    from ..models.models import Image
    from ..database import SessionLocal
    
    if db is None:
        db = SessionLocal()
    
    try:
        capture_time = result.get("captureTime")
        if isinstance(capture_time, str):
            try:
                capture_time = dt.datetime.strptime(capture_time, '%Y-%m-%d %H:%M:%S.%f')
            except ValueError:
                capture_time = dt.datetime.strptime(capture_time, '%Y-%m-%d %H:%M:%S')
        
        image_name = result.get("name", "")
        existing_image = db.query(Image).filter(Image.name == image_name).first()
        
        if existing_image:
            existing_image.hasDefects = result.get("hasDefects", False)
            existing_image.captureTime = capture_time or dt.datetime.now()
            existing_image.detection_total_cnts = result.get("detection_total_cnts", 0)
            existing_image.set_detection_classes(result.get("detection_classes", []))
            existing_image.set_detection_boxes(result.get("detection_boxes", []))
            existing_image.set_detection_scores(result.get("detection_scores", []))
            db.commit()
            db.refresh(existing_image)
            return existing_image
        else:
            new_image = Image(
                name=image_name,
                hasDefects=result.get("hasDefects", False),
                captureTime=capture_time or dt.datetime.now(),
                detection_total_cnts=result.get("detection_total_cnts", 0)
            )
            new_image.set_detection_classes(result.get("detection_classes", []))
            new_image.set_detection_boxes(result.get("detection_boxes", []))
            new_image.set_detection_scores(result.get("detection_scores", []))
            
            db.add(new_image)
            db.commit()
            db.refresh(new_image)
            return new_image
    except Exception as e:
        db.rollback()
        print(f"Failed to save detection result: {e}")
        return None
    finally:
        if db is None:
            db.close()
