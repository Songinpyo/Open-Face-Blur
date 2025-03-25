#!/usr/bin/env python3
"""
Semi-Automatic Face Anonymizer

Entry point for the face anonymization application.
"""

import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.core.face_detector import FaceDetector
from src.core.blur_manager import BlurManager
from src.core.video_processor import VideoProcessor
from src.ui.face_blur_ui import FaceBlurUI

def main():
    """Main entry point for the application"""
    face_detector = FaceDetector(confidence_threshold=0.85)
    blur_manager = BlurManager()
    
    video_processor = VideoProcessor(face_detector, blur_manager)
    video_processor.detect_faces = True
    
    ui = FaceBlurUI(video_processor)
    ui.run()

if __name__ == "__main__":
    main() 