
import os
from ultralytics import YOLO

def train_yolo():
    # Load a model
    model = YOLO('yolov8n.pt')  # or yolov8s.pt, yolov8m.pt, yolov8l.pt, yolov8x.pt
    
    # Train the model
    results = model.train(
        data='datasets\human_tracking_processed/yolo/dataset.yaml',
        epochs=100,
        batch=16,
        imgsz=640,
        device='cpu',  # or 'cuda' if GPU available
        project='datasets\human_tracking_processed/yolo_training',
        name='human_tracking'
    )
    
    print("YOLO training completed!")
    print(f"Results saved to: {results}")

if __name__ == "__main__":
    train_yolo()
