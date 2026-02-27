import datetime as dt
import torch
import os
import json
import requests
from ultralytics import YOLO
import cv2

YOLO_model = None

def _load_model():
    global YOLO_model
    if YOLO_model is None:
        model_path = os.path.join(os.path.dirname(__file__), "best.pt")
        if os.path.exists(model_path):
            YOLO_model = YOLO(model_path)
        else:
            YOLO_model = YOLO("best.pt")
    return YOLO_model


def detect_image(image_path: str, file_name: str) -> dict:
    model = _load_model()
    result = model(image_path)
    
    detection_classes = []
    detection_boxes = []
    detection_scores = []
    k = len(result[0].boxes.cls)
    
    for i in range(k):
        class_name = result[0].names[int(result[0].boxes.cls[i])].capitalize()
        detection_classes.append(class_name)
        detection_boxes.append(result[0].boxes.xyxy[i].tolist())
        score = float(result[0].boxes.conf[i])
        detection_scores.append(score)
    
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
        os.makedirs(export_dir_visuals, exist_ok=True)
        plotted_img = result[0].plot()
        cv2.imwrite(os.path.join(export_dir_visuals, f"{file_name}.png"), plotted_img)
    else:
        temp_dict["hasDefects"] = False
    
    return temp_dict


def save_json(data: dict, output_dir: str, filename: str):
    file_name = data["captureTime"][-8:] + filename
    file_path = os.path.join(output_dir, data["captureTime"][:10], f"{file_name}.json")
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, 'w') as json_file:
        json.dump(data, json_file)


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
        
        new_image = Image(
            name=result.get("name", ""),
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
