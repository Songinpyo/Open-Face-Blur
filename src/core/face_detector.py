import cv2
import numpy as np
import torch
from facenet_pytorch import MTCNN


class FaceDetector:
    """Face detection using MTCNN from facenet-pytorch"""
    
    def __init__(self, confidence_threshold=0.85, device=None):
        torch.manual_seed(42)
        np.random.seed(42)
        
        if device is None:
            self.device = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')
        else:
            self.device = device
            
        print(f"Using device: {self.device}")
        
        self.detector = MTCNN(
            keep_all=True,
            device=self.device,
            post_process=False,
            min_face_size=20,
            thresholds=[0.6, 0.7, 0.7],
            factor=0.709
        )
        self.confidence_threshold = confidence_threshold

    def detect_faces(self, frame):
        """Detect faces in a frame and return boxes with confidence scores"""
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        boxes, probs = self.detector.detect(rgb_frame)
        
        if boxes is not None and len(boxes) > 0:
            mask = probs >= self.confidence_threshold
            boxes = boxes[mask]
            probs = probs[mask]
            
            boxes = boxes.astype(int)
            
            return boxes, probs
        else:
            return None, None 