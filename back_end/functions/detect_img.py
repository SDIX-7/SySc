import datetime as dt
import torch
import requests
import os
import json

from ultralytics import YOLO
YOLO_model = YOLO("../functions/best.pt")  


def detect_img(path,file_name):

    result = YOLO_model(path)

    detection_classes = []
    detection_boxes = []
    detection_scores = []
    k=len(result[0].boxes.cls)

    for i in range(k):
        class_name = result[0].names[int(result[0].boxes.cls[i])].capitalize()
        detection_classes.append(class_name)
        
        detection_boxes.append(result[0].boxes.xyxy[i].tolist())  # 这里的'detection_boxes'是[xmin, ymin, xmax, ymax]
        
        score = float(result[0].boxes.conf[i])
        detection_scores.append(score)
    
    temp_dict = {   "name": file_name,
                    "hasDefects": True,  # 是否有缺陷
                    "captureTime": str(dt.datetime.now()),  # 收录时间，需要转换成字符串格式
                    "detection_total_cnts": k,
                    "detection_classes": detection_classes,
                    "detection_boxes": detection_boxes,
                    "detection_scores": detection_scores,}
    if k>0:
        temp_dict["hasDefects"]=True
        export_dir_visuals= "./static/results/images"
        os.makedirs(export_dir_visuals, exist_ok=True)
        # 使用plot方法保存可视化结果
        plotted_img = result[0].plot()
        import cv2
        cv2.imwrite(os.path.join(export_dir_visuals, f"{file_name}.png"), plotted_img)
    else:
        temp_dict["hasDefects"]=False
    return temp_dict 

def save_json(data, output_dir, filename):
    # 保存JSON文件
    file_name=data["captureTime"][-8:]+filename
    file_path = os.path.join(output_dir, data["captureTime"][:10],f"{file_name}.json")
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, 'w') as json_file:
        json.dump(data, json_file)



def save_detection_result_to_db(result):
    # 调用后端API保存结果
    url = "http://localhost:5000/images/detection_results"
    response = requests.post(url, json=result)
    if response.status_code == 201:
        print("Detection result saved successfully.")
    else:
        print(f"Failed to save detection result: {response.text}")



