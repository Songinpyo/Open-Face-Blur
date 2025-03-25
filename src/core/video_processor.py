import cv2


class VideoProcessor:
    """Handles video frame processing, detection and blur application"""
    
    def __init__(self, face_detector, blur_manager):
        self.face_detector = face_detector
        self.blur_manager = blur_manager
        self.blur_manager.video_processor = self
        
        self.cap = None
        self.frame_count = 0
        self.current_frame_idx = 0
        self.current_frame = None
        self.detected_faces = None
        self.processed_frames = {}
        self.detection_results = {}
        self.detect_faces = True
        
    def open_video(self, video_path):
        """Open a video file and prepare for processing"""
        self.cap = cv2.VideoCapture(video_path)
        if not self.cap.isOpened():
            print(f"Error: Could not open video {video_path}")
            return False
            
        self.frame_count = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
        self.fps = self.cap.get(cv2.CAP_PROP_FPS)
        self.width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
        print(f"Video opened: {video_path}")
        print(f"Frame count: {self.frame_count}")
        print(f"FPS: {self.fps}")
        print(f"Resolution: {self.width}x{self.height}")
        
        self.current_frame_idx = 0
        self.processed_frames = {}
        self.detection_results = {}
        self.detected_faces = None
        
        ret, frame = self.cap.read()
        if ret:
            self.current_frame = frame
            self.current_frame_idx = 0
            self.blur_manager.current_frame_idx = 0
            
            if self.detect_faces:
                boxes, probs = self.face_detector.detect_faces(frame)
                self.detection_results[0] = boxes
                self.detected_faces = boxes
                
        return True
    
    def get_frame(self, frame_idx):
        """Load a specific frame from the video"""
        if self.cap is None:
            return None
            
        if frame_idx < 0 or frame_idx >= self.frame_count:
            return None
            
        self.cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
        
        ret, frame = self.cap.read()
        if not ret:
            return None
            
        self.current_frame = frame
        self.current_frame_idx = frame_idx
        self.blur_manager.current_frame_idx = frame_idx
        
        if frame_idx in self.detection_results:
            self.detected_faces = self.detection_results[frame_idx]
        else:
            if self.detect_faces:
                boxes, probs = self.face_detector.detect_faces(frame)
                self.detection_results[frame_idx] = boxes
                self.detected_faces = boxes
            else:
                self.detected_faces = None
        
        return frame
    
    def process_current_frame(self):
        """Apply blur and draw boxes for the current frame"""
        if self.current_frame is None:
            return None
            
        if self.current_frame_idx in self.processed_frames:
            return self.processed_frames[self.current_frame_idx]
        
        if self.detected_faces is not None:
            if self.current_frame_idx not in self.blur_manager.detected_regions:
                self.blur_manager.detected_regions[self.current_frame_idx] = []
                
                for i, box in enumerate(self.detected_faces):
                    if box is not None:
                        x1, y1, x2, y2 = box
                        self.blur_manager.detected_regions[self.current_frame_idx].append(
                            (x1, y1, x2, y2, self.blur_manager.default_sigma, self.blur_manager.default_ksize)
                        )
        
        processed_frame = self.blur_manager.apply_blur(
            self.current_frame, 
            self.detected_faces,
            self.current_frame_idx
        )
        
        if self.current_frame_idx in self.blur_manager.detected_regions:
            for x1, y1, x2, y2, _, _ in self.blur_manager.detected_regions[self.current_frame_idx]:
                color = (0, 0, 255)  # Red for auto-detected
                cv2.rectangle(processed_frame, (x1, y1), (x2, y2), color, 2)
                cv2.putText(processed_frame, "Auto Blur", (x1, y1-5), cv2.FONT_HERSHEY_SIMPLEX,.5, color, 2)
                cv2.putText(processed_frame, "Click to remove", (x1, y2+15), cv2.FONT_HERSHEY_SIMPLEX, .4, color, 1)
        
        if self.current_frame_idx in self.blur_manager.manual_regions:
            for x1, y1, x2, y2, _, _ in self.blur_manager.manual_regions[self.current_frame_idx]:
                color = (255, 0, 0)  # Blue for manual
                cv2.rectangle(processed_frame, (x1, y1), (x2, y2), color, 2)
                cv2.putText(processed_frame, "Manual Blur", (x1, y1-5), cv2.FONT_HERSHEY_SIMPLEX, .5, color, 2)
                cv2.putText(processed_frame, "Click to remove", (x1, y2+15), cv2.FONT_HERSHEY_SIMPLEX, .4, color, 1)
        
        self.processed_frames[self.current_frame_idx] = processed_frame
        
        return processed_frame
    
    def next_frame(self):
        """Go to next frame"""
        if self.current_frame_idx < self.frame_count - 1:
            return self.get_frame(self.current_frame_idx + 1)
        return None
    
    def prev_frame(self):
        """Go to previous frame"""
        if self.current_frame_idx > 0:
            return self.get_frame(self.current_frame_idx - 1)
        return None
    
    def save_video(self, output_path, progress_callback=None):
        """
        Save the processed video
        
        Args:
            output_path (str): Path to save the video
            progress_callback (function): Callback function for progress updates
            
        Returns:
            bool: True if video saved successfully, False otherwise
        """
        if self.cap is None:
            print("Error: No video loaded")
            return False
            
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(
            output_path, 
            fourcc, 
            self.fps, 
            (self.width, self.height)
        )
        
        current_pos = self.current_frame_idx
        
        try:
            for i in range(self.frame_count):
                frame = self.get_frame(i)
                if frame is None:
                    continue
                    
                if i in self.detection_results:
                    detected_faces = self.detection_results[i]
                else:
                    detected_faces = None
                    
                processed = self.blur_manager.apply_blur(frame, detected_faces, i)
                
                out.write(processed)
                
                if progress_callback:
                    progress_callback(i + 1, self.frame_count)
        finally:
            out.release()
            
            self.get_frame(current_pos)
            
        print(f"Video saved to {output_path}")
        return True 