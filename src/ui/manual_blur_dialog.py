import tkinter as tk
from tkinter import ttk, Scale, Frame, Label


class ManualBlurDialog:
    """
    Dialog for adding a manual blur region
    
    Attributes:
        root (tk.Toplevel): Dialog window
        x1, y1, x2, y2 (int): Region coordinates
        sigma (int): Gaussian blur sigma
        ksize (int): Gaussian blur kernel size
        result (tuple): Result of the dialog (x1, y1, x2, y2, sigma, ksize)
    """
    def __init__(self, parent, x1, y1, x2, y2, default_sigma=30, default_ksize=31):
        self.root = tk.Toplevel(parent)
        self.root.title("Add Manual Blur Region")
        self.root.geometry("350x350")
        self.root.resizable(False, False)
        self.root.transient(parent)
        self.root.grab_set()
        
        self.setup_styles()
        
        self.x1, self.y1, self.x2, self.y2 = x1, y1, x2, y2
        self.sigma = default_sigma
        self.ksize = default_ksize
        self.result = None
        
        self.create_widgets()
        
        self.center_dialog()
        
    def setup_styles(self):
        """Set up UI styles for a cleaner look"""
        bg_color = "#f5f5f5"
        self.root.configure(background=bg_color)
        
        self.style = ttk.Style()
        self.style.configure("TFrame", background=bg_color)
        self.style.configure("TLabel", background=bg_color, font=('Arial', 10))
        self.style.configure("TButton", font=('Arial', 10))
        self.style.configure("Title.TLabel", font=('Arial', 12, 'bold'), padding=5)
        self.style.configure("Region.TLabel", font=('Arial', 10, 'italic'), foreground='#555555')
        
    def center_dialog(self):
        """Center the dialog on parent window"""
        self.root.update_idletasks()
        parent = self.root.master
        
        parent_x = parent.winfo_rootx()
        parent_y = parent.winfo_rooty()
        parent_width = parent.winfo_width()
        parent_height = parent.winfo_height()
        
        dialog_width = self.root.winfo_width()
        dialog_height = self.root.winfo_height()
        
        x = parent_x + (parent_width - dialog_width) // 2
        y = parent_y + (parent_height - dialog_height) // 2
        
        self.root.geometry(f"+{x}+{y}")
        
    def create_widgets(self):
        """Create dialog widgets"""
        main_frame = ttk.Frame(self.root, padding=15)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        title_label = ttk.Label(main_frame, text="Configure Blur Region", style="Title.TLabel")
        title_label.pack(fill=tk.X, pady=(0, 10))
        
        region_text = f"Region: ({self.x1}, {self.y1}) - ({self.x2}, {self.y2})"
        region_label = ttk.Label(main_frame, text=region_text, style="Region.TLabel")
        region_label.pack(fill=tk.X, pady=(0, 15))
        
        sigma_frame = ttk.Frame(main_frame)
        sigma_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(sigma_frame, text="Blur Strength (Sigma):").pack(anchor=tk.W)
        sigma_slider = Scale(
            sigma_frame, from_=1, to=100, orient=tk.HORIZONTAL, length=300,
            command=self.update_sigma, bg="#f5f5f5", highlightthickness=0,
            troughcolor="#dddddd", activebackground="#3498db"
        )
        sigma_slider.set(self.sigma)
        sigma_slider.pack(fill=tk.X, pady=5)
        
        ksize_frame = ttk.Frame(main_frame)
        ksize_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(ksize_frame, text="Blur Size (Kernel Size):").pack(anchor=tk.W)
        ksize_slider = Scale(
            ksize_frame, from_=3, to=101, orient=tk.HORIZONTAL, length=300,
            command=self.update_ksize, bg="#f5f5f5", highlightthickness=0,
            troughcolor="#dddddd", activebackground="#3498db"
        )
        ksize_slider.set(self.ksize)
        ksize_slider.pack(fill=tk.X, pady=5)
        
        if self.ksize % 2 == 0:
            self.ksize += 1
            ksize_slider.set(self.ksize)
        
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=20)
        
        ttk.Button(button_frame, text="OK", command=self.on_ok, width=10).pack(side=tk.LEFT, padx=10)
        ttk.Button(button_frame, text="Cancel", command=self.on_cancel, width=10).pack(side=tk.LEFT, padx=10)
        
        self.root.bind("<Return>", lambda e: self.on_ok())
        self.root.bind("<Escape>", lambda e: self.on_cancel())
        
    def update_sigma(self, value):
        """Update blur sigma"""
        self.sigma = int(value)
        
    def update_ksize(self, value):
        """Update blur kernel size"""
        ksize = int(value)
        self.ksize = ksize if ksize % 2 == 1 else ksize + 1
        
    def on_ok(self):
        """Handle OK button click"""
        self.result = (self.x1, self.y1, self.x2, self.y2, self.sigma, self.ksize)
        self.root.destroy()
        
    def on_cancel(self):
        """Handle Cancel button click"""
        self.root.destroy()
        
    def wait_for_result(self):
        """
        Wait for dialog result
        
        Returns:
            tuple: (x1, y1, x2, y2, sigma, ksize) or None if canceled
        """
        self.root.wait_window()
        return self.result 