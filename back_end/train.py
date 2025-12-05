from ultralytics import YOLO

if __name__ == '__main__':
    # Load a model
    model = YOLO("yolov8s-p2.yaml")  # build a new model from YAML
    # Train the model
    results = model.train(data="D:/质量信息系统/flask+vue/back_end/dataset_split/PCB.yaml", epochs=100, imgsz=1280,device='cuda',batch=-1)
