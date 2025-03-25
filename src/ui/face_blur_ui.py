import tkinter as tk
from tkinter import filedialog, Scale, Button, Frame, Label, Checkbutton, IntVar, StringVar, ttk
from PIL import Image, ImageTk
import cv2
import threading
import queue
import time

from .manual_blur_dialog import ManualBlurDialog


class FaceBlurUI:
    """
    User interface for the face blurring application
    
    Attributes:
        root (tk.Tk): Root window
        video_processor (VideoProcessor): Video processor object
        draw_mode (bool): Whether we're in manual region drawing mode
        start_x, start_y (int): Starting coordinates for manual region
    """
    def __init__(self, video_processor):
        self.video_processor = video_processor
        self.blur_manager = video_processor.blur_manager
        
        self.root = tk.Tk()
        self.root.title("Face Blur Tool")
        self.root.geometry("1200x800")
        
        self.setup_styles()
        
        self.drawing = False
        self.start_x = 0
        self.start_y = 0
        self.rect_id = None
        self.blur_sigma = IntVar(value=self.blur_manager.default_sigma)
        self.blur_ksize = IntVar(value=self.blur_manager.default_ksize)
        self.current_frame_var = StringVar(value="0 / 0")
        self.slider_value_var = StringVar(value="0 / 0")
        self.detection_status_var = StringVar(value="")
        self.processing_queue = queue.Queue()
        self.processing_thread = None
        self.is_processing = False
        self.auto_detect = True
        self.display_scale_x = 1.0
        self.display_scale_y = 1.0
        
        self.create_ui()
        
        self.setup_shortcuts()
        
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
    
    def setup_styles(self):
        """Set up UI styles for a cleaner, more modern look"""
        bg_color = "#f0f0f0"
        accent_color = "#2c3e50"
        button_bg = "#3498db"
        
        self.root.configure(background=bg_color)
        
        self.style = ttk.Style()
        
        self.style.configure('TButton', 
                            background=button_bg,
                            foreground="black",
                            font=('Arial', 10))
                            
        self.style.configure('TFrame', background=bg_color)
        self.style.configure('TLabel', 
                            background=bg_color, 
                            foreground=accent_color, 
                            font=('Arial', 10))
        self.style.configure('TScale',
                            background=bg_color)
        
        self.style.configure('Counter.TLabel',
                            background=bg_color,
                            foreground="#e74c3c",
                            font=('Arial', 12, 'bold'))
        
        self.style.configure('Detection.TLabel',
                           background="#ecf0f1", 
                           foreground="#e74c3c",
                           font=('Arial', 10, 'bold'))
        
        self.style.configure('StatusBar.TLabel',
                            background="#ecf0f1",
                            foreground="#34495e",
                            relief=tk.SUNKEN,
                            font=('Arial', 9))
        
        self.style.configure('Draw.TButton',
                            background="#e74c3c",
                            foreground="black")
                            
        self.style.configure('Detect.TButton',
                            background="#27ae60",
                            foreground="black")
                            
        self.style.configure('Maintain.TButton',
                            background="#9b59b6",
                            foreground="black")
        
        self.style.configure('Help.TLabel',
                           background="#ecf0f1",
                           foreground="#34495e",
                           font=('Arial', 10))
        
    def setup_shortcuts(self):
        """Set up keyboard shortcuts"""
        # Bind key events to root window
        self.root.bind("<o>", lambda e: self.open_video())
        self.root.bind("<s>", lambda e: self.save_video())
        self.root.bind("<d>", lambda e: self.next_frame())
        self.root.bind("<a>", lambda e: self.prev_frame())
        self.root.bind("<q>", lambda e: self.toggle_auto_detect())
        self.root.bind("<r>", lambda e: self.run_detection())
        self.root.bind("<f>", lambda e: self.maintain_prev_box())
        self.root.bind("<Left>", lambda e: self.prev_frame())
        self.root.bind("<Right>", lambda e: self.next_frame())
        self.root.bind("<Escape>", lambda e: self.cancel_drawing())
        
    def cancel_drawing(self):
        """Cancel current drawing operation"""
        if self.drawing:
            self.drawing = False
            if self.rect_id:
                self.canvas.delete(self.rect_id)
                self.rect_id = None
            
            self.detection_status_var.set("Drawing canceled")
            self.root.after(1500, lambda: self.detection_status_var.set(""))
    
    def toggle_auto_detect(self):
        """Toggle auto detect mode"""
        self.auto_detect = not self.auto_detect
        if self.auto_detect:
            self.detect_button.config(text="Auto Detect: ON (Q)")
            if self.video_processor.current_frame is not None:
                self.detection_status_var.set("Auto-detect ON")
                self.root.after(1500, lambda: self.detection_status_var.set(""))
                
                self.video_processor.detect_faces = True
                
                current_idx = self.video_processor.current_frame_idx
                if current_idx in self.video_processor.detection_results:
                    del self.video_processor.detection_results[current_idx]
                self.run_detection()
        else:
            self.detect_button.config(text="Auto Detect: OFF (Q)")
            self.detection_status_var.set("Auto-detect OFF")
            self.root.after(1500, lambda: self.detection_status_var.set(""))
            
            self.video_processor.detect_faces = False
        
    def run_detection(self):
        """Run face detection on current frame"""
        if self.video_processor.current_frame is not None:
            self.detection_status_var.set("Detecting faces...")
            
            self.root.update_idletasks()
            
            current_idx = self.video_processor.current_frame_idx
            if current_idx in self.video_processor.detection_results:
                del self.video_processor.detection_results[current_idx]
            
            frame = self.video_processor.current_frame
            boxes, probs = self.video_processor.face_detector.detect_faces(frame)
            self.video_processor.detection_results[current_idx] = boxes
            self.video_processor.detected_faces = boxes
            
            num_faces = 0 if boxes is None else len(boxes)
            self.detection_status_var.set(f"Found {num_faces} faces")
            
            self.root.after(3000, lambda: self.detection_status_var.set(""))
            
            if current_idx in self.video_processor.processed_frames:
                del self.video_processor.processed_frames[current_idx]
            self.show_frame()
        
    def create_ui(self):
        """Create UI elements"""
        top_frame = ttk.Frame(self.root, padding="10 10 10 5")
        top_frame.pack(fill=tk.X)
        
        frame_counter_frame = ttk.Frame(top_frame, padding="5")
        frame_counter_frame.pack(side=tk.TOP, fill=tk.X, pady=(0, 10))
        
        self.frame_counter = ttk.Label(
            frame_counter_frame, 
            textvariable=self.current_frame_var, 
            style="Counter.TLabel",
            anchor=tk.CENTER
        )
        self.frame_counter.pack(fill=tk.X)
        
        control_frame = ttk.Frame(self.root, padding="10 5 10 10")
        control_frame.pack(fill=tk.X)
        
        self.canvas_frame = ttk.Frame(self.root, padding="10")
        self.canvas_frame.pack(fill=tk.BOTH, expand=True)
        
        self.canvas = tk.Canvas(self.canvas_frame, bg="#1e1e1e", highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        self.canvas.bind("<Button-1>", self.on_canvas_click)
        self.canvas.bind("<B1-Motion>", self.on_canvas_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_canvas_release)
        
        self.status_bar = ttk.Label(self.root, text="No video loaded", style='StatusBar.TLabel', anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        draw_help_frame = ttk.Frame(self.root, padding="10 5 10 0")
        draw_help_frame.pack(side=tk.BOTTOM, fill=tk.X)
        
        draw_help_text = ttk.Label(
            draw_help_frame,
            text="🖱️ Click & drag to add blur region  |  Click on colored region to remove blur  |  Press ESC to cancel drawing",
            style="Help.TLabel",
            anchor=tk.CENTER
        )
        draw_help_text.pack(fill=tk.X)
        
        button_frame = ttk.Frame(top_frame)
        button_frame.pack(side=tk.LEFT)
        
        ttk.Button(button_frame, text="Open Video (O)", command=self.open_video).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Save Video (S)", command=self.save_video).pack(side=tk.LEFT, padx=5)
        
        self.maintain_box_btn = ttk.Button(button_frame, text="Maintain Prev Box (F)", 
                                         command=self.maintain_prev_box, style='Maintain.TButton')
        self.maintain_box_btn.pack(side=tk.LEFT, padx=5)
        
        self.detect_button = ttk.Button(button_frame, text="Auto Detect: ON (Q)", 
                                      command=self.toggle_auto_detect, style='Detect.TButton')
        self.detect_button.pack(side=tk.LEFT, padx=5)
        
        run_detect_btn = ttk.Button(button_frame, text="Run Detection (R)", 
                 command=self.run_detection)
        run_detect_btn.pack(side=tk.LEFT, padx=5)
        
        self.detection_status_label = ttk.Label(
            button_frame, 
            textvariable=self.detection_status_var,
            style="Detection.TLabel",
            width=15
        )
        self.detection_status_label.pack(side=tk.LEFT, padx=5)
        
        progress_frame = ttk.Frame(top_frame)
        progress_frame.pack(side=tk.RIGHT)
        
        self.progress_label = ttk.Label(progress_frame, text="")
        self.progress_label.pack(side=tk.RIGHT, padx=5)
        
        nav_frame = ttk.Frame(control_frame)
        nav_frame.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(nav_frame, text="◀ Previous (A)", command=self.prev_frame).pack(side=tk.LEFT, padx=5)
        ttk.Button(nav_frame, text="Next (D) ▶", command=self.next_frame).pack(side=tk.LEFT, padx=5)
        
        blur_frame = ttk.Frame(control_frame)
        blur_frame.pack(side=tk.LEFT, padx=20)
        
        blur_title_frame = ttk.Frame(blur_frame)
        blur_title_frame.pack(fill=tk.X, pady=5)
        ttk.Label(blur_title_frame, text="Blur Controls", font=('Arial', 11, 'bold')).pack(anchor=tk.W)
        
        blur_sigma_frame = ttk.Frame(blur_frame)
        blur_sigma_frame.pack(fill=tk.X, pady=2)
        ttk.Label(blur_sigma_frame, text="Blur Strength:").pack(side=tk.LEFT)
        
        sigma_slider = ttk.Scale(
            blur_frame, from_=1, to=100, orient=tk.HORIZONTAL, 
            variable=self.blur_sigma, command=self.update_blur_params,
            length=200
        )
        sigma_slider.pack(pady=5)
        
        self.sigma_value_label = ttk.Label(blur_frame, text=f"Value: {self.blur_sigma.get()}")
        self.sigma_value_label.pack(anchor=tk.W, pady=(0, 5))
        
        blur_ksize_frame = ttk.Frame(blur_frame)
        blur_ksize_frame.pack(fill=tk.X, pady=2)
        ttk.Label(blur_ksize_frame, text="Blur Size:").pack(side=tk.LEFT)
        
        ksize_slider = ttk.Scale(
            blur_frame, from_=3, to=101, orient=tk.HORIZONTAL, 
            variable=self.blur_ksize, command=self.update_blur_params,
            length=200
        )
        ksize_slider.pack(pady=5)
        
        self.ksize_value_label = ttk.Label(blur_frame, text=f"Value: {self.blur_ksize.get()}")
        self.ksize_value_label.pack(anchor=tk.W, pady=(0, 5))
        
        frame_nav_frame = ttk.Frame(control_frame)
        frame_nav_frame.pack(side=tk.RIGHT, padx=10)
        
        ttk.Label(frame_nav_frame, text="Frame:").pack(side=tk.LEFT)
        
        slider_frame = ttk.Frame(frame_nav_frame)
        slider_frame.pack(side=tk.RIGHT)
        
        self.frame_slider = ttk.Scale(
            slider_frame, from_=0, to=100, orient=tk.HORIZONTAL, 
            length=400, command=self.on_slider_change
        )
        self.frame_slider.pack(side=tk.TOP, padx=10)
        
        self.slider_value_label = ttk.Label(slider_frame, textvariable=self.slider_value_var, anchor=tk.CENTER)
        self.slider_value_label.pack(side=tk.TOP, fill=tk.X)
        
        self.disable_ui()
        
    def disable_ui(self):
        """Disable UI elements when no video is loaded"""
        self.frame_slider.state(['disabled'])
        self.canvas.config(state=tk.DISABLED)
        
    def enable_ui(self):
        """Enable UI elements when video is loaded"""
        self.frame_slider.state(['!disabled'])
        self.canvas.config(state=tk.NORMAL)
        
        total_frames = self.video_processor.frame_count
        self.frame_slider.config(from_=0, to=total_frames-1)
        self.slider_value_var.set(f"0 / {total_frames-1}")
        
    def open_video(self):
        """Open a video file"""
        video_path = filedialog.askopenfilename(
            title="Select Video File",
            filetypes=(
                ("Video Files", "*.mp4 *.avi *.mov *.mkv"),
                ("All Files", "*.*")
            )
        )
        
        if not video_path:
            return
        
        self.video_processor.detect_faces = self.auto_detect
        
        if self.video_processor.open_video(video_path):
            self.enable_ui()
            
            self.update_status()
            
            if not self.auto_detect:
                self.video_processor.detect_faces = False
                self.detection_status_var.set("Auto-detect OFF")
                self.root.after(2000, lambda: self.detection_status_var.set(""))
            else:
                self.detection_status_var.set("Detecting faces...")
                self.root.update_idletasks()
                self.root.after(2000, lambda: self.detection_status_var.set("Ready"))
                self.root.after(3500, lambda: self.detection_status_var.set(""))
            
            self.show_frame()
            
    def save_video(self):
        """Save processed video"""
        if self.video_processor.cap is None:
            return
            
        output_path = filedialog.asksaveasfilename(
            title="Save Video As",
            defaultextension=".mp4",
            filetypes=(
                ("MP4 Video", "*.mp4"),
                ("AVI Video", "*.avi"),
                ("All Files", "*.*")
            )
        )
        
        if not output_path:
            return
            
        if not self.is_processing:
            self.is_processing = True
            self.processing_thread = threading.Thread(
                target=self.process_video_thread,
                args=(output_path,)
            )
            self.processing_thread.daemon = True
            self.processing_thread.start()
            
            self.root.after(100, self.check_progress)
            
    def process_video_thread(self, output_path):
        """Thread for processing and saving video"""
        try:
            def progress_callback(current, total):
                progress = int(current / total * 100)
                self.processing_queue.put(("progress", progress))
                
            result = self.video_processor.save_video(output_path, progress_callback)
            
            if result:
                self.processing_queue.put(("complete", "Video saved successfully"))
            else:
                self.processing_queue.put(("error", "Error saving video"))
        except Exception as e:
            self.processing_queue.put(("error", f"Error: {str(e)}"))
        finally:
            self.is_processing = False
            
    def check_progress(self):
        """Check progress of video processing"""
        try:
            while True:
                msg_type, msg = self.processing_queue.get_nowait()
                
                if msg_type == "progress":
                    self.progress_label.config(text=f"Processing: {msg}%")
                elif msg_type == "complete":
                    self.progress_label.config(text="Complete")
                    self.root.after(3000, lambda: self.progress_label.config(text=""))
                    return
                elif msg_type == "error":
                    self.progress_label.config(text=msg)
                    self.root.after(3000, lambda: self.progress_label.config(text=""))
                    return
                    
                self.processing_queue.task_done()
        except queue.Empty:
            if self.is_processing:
                self.root.after(100, self.check_progress)
                
    def update_blur_params(self, _=None):
        """Update blur parameters"""
        sigma = self.blur_sigma.get()
        ksize = self.blur_ksize.get()
        
        if ksize % 2 == 0:
            ksize += 1
            self.blur_ksize.set(ksize)
            
        self.blur_manager.update_blur_params(sigma, ksize)
        
        self.sigma_value_label.config(text=f"Value: {sigma}")
        self.ksize_value_label.config(text=f"Value: {ksize}")
        
        self.video_processor.processed_frames = {}
        
        self.show_frame()
            
    def on_slider_change(self, value):
        """Handle frame slider change"""
        frame_idx = int(float(value))
        max_idx = self.video_processor.frame_count - 1
        
        self.slider_value_var.set(f"{frame_idx} / {max_idx}")
        
        self.video_processor.get_frame(frame_idx)
        
        self.show_frame()
        
        self.update_status()
            
    def on_canvas_click(self, event):
        """Handle canvas click"""
        if self.video_processor.cap is None:
            return
            
        frame_height, frame_width = self.video_processor.current_frame.shape[:2]
        
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        
        img_width = int(frame_width * self.display_scale_x)
        img_height = int(frame_height * self.display_scale_y)
        
        offset_x = (canvas_width - img_width) // 2
        offset_y = (canvas_height - img_height) // 2
        
        adj_x = event.x - offset_x
        adj_y = event.y - offset_y
        
        if adj_x < 0 or adj_x >= img_width or adj_y < 0 or adj_y >= img_height:
            return
        
        x = int(adj_x / self.display_scale_x)
        y = int(adj_y / self.display_scale_y)
        
        result = self.blur_manager.toggle_region(x, y, self.video_processor.detected_faces)
        if result:
            current_idx = self.video_processor.current_frame_idx
            if current_idx in self.video_processor.processed_frames:
                del self.video_processor.processed_frames[current_idx]
            
            self.detection_status_var.set("Region removed")
            self.root.after(1500, lambda: self.detection_status_var.set(""))
            
            self.show_frame()
        else:
            self.drawing = True
            self.start_x = x
            self.start_y = y
                
    def on_canvas_drag(self, event):
        """Handle canvas drag for drawing regions"""
        if not self.drawing:
            return
            
        frame_height, frame_width = self.video_processor.current_frame.shape[:2]
        
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        
        img_width = int(frame_width * self.display_scale_x)
        img_height = int(frame_height * self.display_scale_y)
        
        offset_x = (canvas_width - img_width) // 2
        offset_y = (canvas_height - img_height) // 2
        
        adj_x = event.x - offset_x
        adj_y = event.y - offset_y
        
        adj_x = max(0, min(adj_x, img_width - 1))
        adj_y = max(0, min(adj_y, img_height - 1))
        
        x = int(adj_x / self.display_scale_x)
        y = int(adj_y / self.display_scale_y)
        
        if self.rect_id:
            self.canvas.delete(self.rect_id)
            
        canvas_start_x = self.start_x * self.display_scale_x + offset_x
        canvas_start_y = self.start_y * self.display_scale_y + offset_y
        canvas_x = adj_x + offset_x
        canvas_y = adj_y + offset_y
        
        self.rect_id = self.canvas.create_rectangle(
            canvas_start_x, canvas_start_y, canvas_x, canvas_y,
            outline="#e74c3c", width=2, dash=(5, 5)
        )
        
    def on_canvas_release(self, event):
        """Handle canvas release for adding manual regions"""
        if not self.drawing:
            return
            
        self.drawing = False
        
        frame_height, frame_width = self.video_processor.current_frame.shape[:2]
        
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        
        img_width = int(frame_width * self.display_scale_x)
        img_height = int(frame_height * self.display_scale_y)
        
        offset_x = (canvas_width - img_width) // 2
        offset_y = (canvas_height - img_height) // 2
        
        adj_x = event.x - offset_x
        adj_y = event.y - offset_y
        
        adj_x = max(0, min(adj_x, img_width - 1))
        adj_y = max(0, min(adj_y, img_height - 1))
        
        end_x = int(adj_x / self.display_scale_x)
        end_y = int(adj_y / self.display_scale_y)
        
        x1 = min(self.start_x, end_x)
        y1 = min(self.start_y, end_y)
        x2 = max(self.start_x, end_x)
        y2 = max(self.start_y, end_y)
        
        if x2 - x1 < 10 or y2 - y1 < 10:
            if self.rect_id:
                self.canvas.delete(self.rect_id)
                self.rect_id = None
            return
        
        if self.rect_id:
            self.canvas.delete(self.rect_id)
            self.rect_id = None
            
        sigma = self.blur_sigma.get()
        ksize = self.blur_ksize.get()
        # Ensure ksize is odd
        ksize = ksize if ksize % 2 == 1 else ksize + 1
        
        frame_idx = self.video_processor.current_frame_idx
        self.blur_manager.add_manual_region_to_frame(frame_idx, x1, y1, x2, y2, sigma, ksize)
        
        if frame_idx in self.video_processor.processed_frames:
            del self.video_processor.processed_frames[frame_idx]
        
        self.show_frame()
        
    def next_frame(self):
        """Go to next frame"""
        frame = self.video_processor.next_frame()
        if frame is not None:
            self.detection_status_var.set("")
            
            current_idx = self.video_processor.current_frame_idx
            if current_idx in self.video_processor.processed_frames:
                del self.video_processor.processed_frames[current_idx]
                
            self.show_frame()
            self.update_status()
            
            frame_idx = self.video_processor.current_frame_idx
            self.frame_slider.set(frame_idx)
            self.slider_value_var.set(f"{frame_idx} / {self.video_processor.frame_count-1}")
            
    def prev_frame(self):
        """Go to previous frame"""
        frame = self.video_processor.prev_frame()
        if frame is not None:
            self.detection_status_var.set("")
            
            self.show_frame()
            self.update_status()
            
            frame_idx = self.video_processor.current_frame_idx
            self.frame_slider.set(frame_idx)
            self.slider_value_var.set(f"{frame_idx} / {self.video_processor.frame_count-1}")
            
    def show_frame(self):
        """Show the current frame"""
        if self.video_processor.current_frame is None:
            return
        
        processed = self.video_processor.process_current_frame()
        
        img = cv2.cvtColor(processed, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(img)
        
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        
        if canvas_width > 1 and canvas_height > 1:
            img_height, img_width = processed.shape[:2]
            
            scale_x = canvas_width / img_width
            scale_y = canvas_height / img_height
            scale = min(scale_x, scale_y)
            
            self.display_scale_x = scale
            self.display_scale_y = scale
            
            new_width = int(img_width * scale)
            new_height = int(img_height * scale)
            img = img.resize((new_width, new_height), Image.LANCZOS)
        
        self.photo = ImageTk.PhotoImage(img)
        
        self.canvas.delete("all")
        self.canvas.create_image(
            canvas_width // 2, canvas_height // 2,
            image=self.photo,
            anchor=tk.CENTER
        )
        
        current = self.video_processor.current_frame_idx
        total = self.video_processor.frame_count - 1
        self.current_frame_var.set(f"Frame: {current} / {total}")
            
    def update_status(self):
        """Update status bar"""
        if self.video_processor.cap is None:
            self.status_bar.config(text="No video loaded")
            return
            
        current = self.video_processor.current_frame_idx
        total = self.video_processor.frame_count - 1
        fps = self.video_processor.fps
        
        status = f"Frame: {current}/{total} | FPS: {fps:.2f}"
        
        if self.video_processor.detected_faces is not None:
            num_faces = len(self.video_processor.detected_faces)
            status += f" | Detected faces: {num_faces}"
            
        if self.auto_detect:
            status += " | Auto-Detect: ON"
        else:
            status += " | Auto-Detect: OFF"
            
        has_manual = self.blur_manager.current_frame_idx in self.blur_manager.manual_regions and len(self.blur_manager.manual_regions[self.blur_manager.current_frame_idx]) > 0
        has_detected = self.blur_manager.current_frame_idx in self.blur_manager.detected_regions and len(self.blur_manager.detected_regions[self.blur_manager.current_frame_idx]) > 0
        
        if has_manual:
            num_manual = len(self.blur_manager.manual_regions[self.blur_manager.current_frame_idx])
            status += f" | Manual regions: {num_manual}"
            
        if has_detected:
            num_detected = len(self.blur_manager.detected_regions[self.blur_manager.current_frame_idx])
            status += f" | Detected blur regions: {num_detected}"
            
        self.status_bar.config(text=status)
        
    def on_close(self):
        """Handle window close"""
        if self.video_processor.cap is not None:
            self.video_processor.cap.release()
            
        self.root.destroy()
        
    def run(self):
        """Run the application"""
        self.root.mainloop()
        
    def maintain_prev_box(self):
        """Copy regions from current frame to next frame and move to next frame"""
        if self.video_processor.cap is None:
            return
            
        current_idx = self.video_processor.current_frame_idx
        next_idx = current_idx + 1
        
        if next_idx >= self.video_processor.frame_count:
            self.detection_status_var.set("Last frame reached")
            self.root.after(1500, lambda: self.detection_status_var.set(""))
            return
            
        if self.blur_manager.copy_regions_to_next_frame():
            self.detection_status_var.set("Regions copied to next frame")
            
            if next_idx in self.video_processor.processed_frames:
                del self.video_processor.processed_frames[next_idx]
                
            self.video_processor.get_frame(next_idx)
            
            self.show_frame()
            
            self.update_status()
            self.frame_slider.set(next_idx)
            self.slider_value_var.set(f"{next_idx} / {self.video_processor.frame_count-1}")
            
            self.root.after(1500, lambda: self.detection_status_var.set(""))
        else:
            self.detection_status_var.set("No regions to copy")
            
            self.next_frame()
            
            self.root.after(1500, lambda: self.detection_status_var.set("")) 