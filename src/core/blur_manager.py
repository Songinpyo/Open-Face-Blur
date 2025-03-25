import cv2


class BlurManager:
    """Manages blur regions for both automatic and manual selections"""
    
    def __init__(self):
        self.blur_regions = []
        self.manual_regions = {}
        self.detected_regions = {}
        self.all_blurred = True
        
        # Default blur parameters for anonymization
        self.default_sigma = 30
        self.default_ksize = 31  # Must be odd number
        
        self.blurred_face_indices = set()
        self.current_frame_idx = 0
        
    def reset(self):
        """Reset all blur settings to default"""
        self.blur_regions = []
        self.manual_regions = {}
        self.detected_regions = {}
        self.all_blurred = True
        self.blurred_face_indices = set()
        
    def toggle_all_blur(self):
        """Toggle blur for all detected faces"""
        self.all_blurred = not self.all_blurred
        
    def toggle_region(self, x, y, detected_faces):
        """Remove blur region at the given x,y point"""
        if self.current_frame_idx in self.detected_regions:
            for i, region in enumerate(self.detected_regions[self.current_frame_idx]):
                x1, y1, x2, y2, _, _ = region
                if x1 <= x <= x2 and y1 <= y <= y2:
                    self.detected_regions[self.current_frame_idx].pop(i)
                    return True
        
        if self.current_frame_idx in self.manual_regions:
            for i, region in enumerate(self.manual_regions[self.current_frame_idx]):
                x1, y1, x2, y2, _, _ = region
                if x1 <= x <= x2 and y1 <= y <= y2:
                    self.manual_regions[self.current_frame_idx].pop(i)
                    return True
                    
        return False
    
    def add_manual_region(self, x1, y1, x2, y2, sigma, ksize):
        """Legacy method - use add_manual_region_to_frame instead"""
        frame_idx = getattr(getattr(self, 'video_processor', None), 'current_frame_idx', None)
        if frame_idx is not None:
            self.add_manual_region_to_frame(frame_idx, x1, y1, x2, y2, sigma, ksize)
        
    def add_manual_region_to_frame(self, frame_idx, x1, y1, x2, y2, sigma, ksize):
        """Add a user-defined blur region to a specific frame"""
        if frame_idx not in self.manual_regions:
            self.manual_regions[frame_idx] = []
        
        self.manual_regions[frame_idx].append((x1, y1, x2, y2, sigma, ksize))
    
    def update_blur_params(self, sigma, ksize):
        """Update blur strength for all regions"""
        self.default_sigma = sigma
        self.default_ksize = ksize
        
        for i in range(len(self.blur_regions)):
            x1, y1, x2, y2, _, _ = self.blur_regions[i]
            self.blur_regions[i] = (x1, y1, x2, y2, sigma, ksize)
            
        for frame_idx in self.manual_regions:
            for i in range(len(self.manual_regions[frame_idx])):
                x1, y1, x2, y2, _, _ = self.manual_regions[frame_idx][i]
                self.manual_regions[frame_idx][i] = (x1, y1, x2, y2, sigma, ksize)
    
    def copy_regions_to_next_frame(self):
        """Copy all blur regions from current frame to next frame"""
        next_frame_idx = self.current_frame_idx + 1
        
        has_manual = self.current_frame_idx in self.manual_regions and len(self.manual_regions[self.current_frame_idx]) > 0
        has_detected = self.current_frame_idx in self.detected_regions and len(self.detected_regions[self.current_frame_idx]) > 0
        
        if not (has_manual or has_detected):
            return False
            
        if has_manual:
            if next_frame_idx not in self.manual_regions:
                self.manual_regions[next_frame_idx] = []
                
            for region in self.manual_regions[self.current_frame_idx]:
                if region not in self.manual_regions[next_frame_idx]:
                    self.manual_regions[next_frame_idx].append(region)
                    
        if has_detected:
            if next_frame_idx not in self.detected_regions:
                self.detected_regions[next_frame_idx] = []
                
            for region in self.detected_regions[self.current_frame_idx]:
                if region not in self.detected_regions[next_frame_idx]:
                    self.detected_regions[next_frame_idx].append(region)
                    
        return True
    
    def apply_blur(self, frame, detected_faces, frame_idx=None):
        """Apply all blur regions to a frame"""
        result = frame.copy()
        
        if frame_idx is not None:
            self.current_frame_idx = frame_idx
        
        if frame_idx in self.detected_regions:
            for x1, y1, x2, y2, sigma, ksize in self.detected_regions[frame_idx]:
                # Ensure ksize is odd
                ksize = ksize if ksize % 2 == 1 else ksize + 1
                
                region = result[y1:y2, x1:x2]
                blurred = cv2.GaussianBlur(region, (ksize, ksize), sigma)
                result[y1:y2, x1:x2] = blurred
        
        if frame_idx is not None and frame_idx in self.manual_regions:
            for x1, y1, x2, y2, sigma, ksize in self.manual_regions[frame_idx]:
                # Ensure ksize is odd
                ksize = ksize if ksize % 2 == 1 else ksize + 1
                
                region = result[y1:y2, x1:x2]
                blurred = cv2.GaussianBlur(region, (ksize, ksize), sigma)
                result[y1:y2, x1:x2] = blurred
            
        return result

    def is_face_blurred(self, face_idx):
        """
        Check if a specific face is blurred
        
        Args:
            face_idx (int): Index of the face
            
        Returns:
            bool: True if the face is blurred
        """
        return face_idx in self.blurred_face_indices 