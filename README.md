# ✨ OpenFaceBlur: Open Source Video Face Anonymization Tool

A Python application for selectively blurring faces in videos with an interactive GUI.

## 💡 Key Features

- **🤖 Deep Learning Based Auto-Blurring** - Automatically detect and blur faces in videos
- **🚫 Easy Removal of Unwanted Blurs** - Remove unnecessary blur regions with a single click
- **🔍 Manual Blurring for Missed Faces** - Add blurs to faces that weren't automatically detected
- **🎮 Intuitive User Interface** - Easy-to-use interface for anyone

## 🎬 Preview

<p align="center">
  <img src="assets/demo.gif" width="80%" alt="Face Blurring Demo">
</p>


## 🚀 Installation

### 📋 Requirements

- Python 3.8
- Conda package manager

### 📦 Dependencies

- PyTorch 1.13.1
- torchvision 0.14.1
- facenet-pytorch 2.5.2
- opencv-python 4.7.0
- pillow 9.4.0
- numpy 1.24.1

### 📥 Step 1: Clone the repository or download the source code

```bash
git clone https://github.com/yourusername/face-blur-framework.git
cd face-blur-framework
```

### 🔨 Step 2: Create and activate a Conda environment

```bash
# Create a new Conda environment named "faceblur" with Python 3.8
conda create -n faceblur python=3.8
conda activate faceblur
```

### 📚 Step 3: Install dependencies with Conda and pip

```bash
# Install PyTorch, torchvision and CUDA toolkit
pip install torch==1.13.1 torchvision==0.14.1

# Install remaining dependencies through pip
pip install facenet-pytorch==2.5.2
pip install opencv-python==4.7.0.72
pip install pillow==9.4.0
pip install numpy==1.24.1
```

### 💻 Alternative Install for CPU-Only (no GPU)

```bash
# Create environment
conda create -n faceblur python=3.8
conda activate faceblur

# Install CPU-only PyTorch
conda install pytorch=1.13.1 torchvision=0.14.1 cpuonly -c pytorch

# Install remaining dependencies
pip install facenet-pytorch==2.5.2
pip install opencv-python==4.7.0.72
pip install pillow==9.4.0
pip install numpy==1.24.1
```

### ✅ Step 4: Verify installation

To verify that the dependencies are installed correctly:

```bash
python -c "import torch; import torchvision; import facenet_pytorch; import cv2; import PIL; import numpy; print('All dependencies installed successfully!')"
```

## 📖 Usage

### 🏃‍♂️ Running the Application

```bash
python face_blur.py
```

### ⌨️ Keyboard Shortcuts

The application provides convenient keyboard shortcuts for quick operation:

| Key       | Action                                    |
|-----------|-------------------------------------------|
| O         | 📂 Open a video file                      |
| S         | 💾 Save processed video                   |
| A         | ⏮️ Previous frame                         |
| D         | ⏭️ Next frame                            |
| F         | 📋 Copy regions to next frame & move forward |
| Q         | 🔄 Toggle auto-detect faces mode (on/off) |
| R         | 🔍 Run face detection on current frame    |
| Left Arrow| ⏮️ Previous frame (alternative)           |
| Right Arrow| ⏭️ Next frame (alternative)              |

### Using the Interface

#### 🎬 Loading & Managing Videos

- **Open Video** 📂
  - Click the "Open Video (O)" button in the top bar
  - Select your video file (supported formats: mp4, avi, mov, mkv)
  - The first frame will load with detected faces automatically blurred

- **Save Video** 💾
  - Click the "Save Video (S)" button
  - Choose a filename and location
  - A progress bar will show processing status
  - The video will be saved with all blur regions applied to all frames

#### 🔍 Navigating Through Frames

- **Frame Navigation** ⏮️ ⏭️
  - Click "Previous (A)" or "Next (D)" buttons to move between frames
  - Use the slider at the bottom to jump to a specific frame
  - Press A/D keys or Left/Right arrow keys for quick navigation
  - Current frame number and total frames are displayed at the top

- **Copy Regions** 📋
  - Click "Maintain Prev Box (F)" button to copy all blur regions to the next frame
  - The application will automatically move to the next frame
  - This is useful for tracking faces across multiple frames

#### 🔎 Face Detection

- **Auto Detect** 🔄
  - Toggle "Auto Detect (Q)" on/off to control automatic face detection
  - When ON: faces are automatically detected and blurred in each frame
  - When OFF: no automatic detection occurs (useful for manual work)

- **Run Detection** 🔍
  - Click "Run Detection (R)" to detect faces in the current frame only
  - Useful when Auto Detect is OFF but you want to detect faces in a specific frame

#### 🎭 Blur Management

- **Adding Blur Regions** ✏️
  - Simply click and drag anywhere on the frame to create a manual blur region
  - Manual regions appear with blue outlines labeled "Manual Blur"
  - Detected face regions appear with red outlines labeled "Auto Blur"
  - Press ESC to cancel drawing

- **Removing Blur** 🗑️
  - Click on any blur region (auto or manual) to remove it
  - The region will be immediately removed from the current frame only

- **Adjusting Blur Parameters** ⚙️
  - Use the "Blur Strength" slider to control blur intensity (sigma)
  - Use the "Blur Size" slider to control blur radius (kernel size)
  - Changes apply to newly created blur regions

#### 📊 Status Information

- The status bar at the bottom shows:
  - Current frame / total frames
  - FPS of the video
  - Number of detected faces
  - Auto-detect status
  - Number of manual and auto blur regions in the current frame

## 🔧 Technical Details

### 🧩 Components

- **🧠 FaceDetector**: Uses MTCNN (Multi-task Cascaded Convolutional Networks) for robust face detection
- **🌫️ BlurManager**: Manages both automatically detected and manually created blur regions
- **🎞️ VideoProcessor**: Handles video I/O and frame processing
- **🖌️ ManualBlurDialog**: User interface for configuring manual blur regions
- **🖥️ FaceBlurUI**: Main application interface

### ⚡ Performance Tips

- 🚀 Face detection results are cached to improve performance
- 💨 Processed frames are cached for quick navigation
- 🧵 Video saving is done in a background thread to keep UI responsive
- ⚠️ Large or high-resolution videos may take longer to process
- 🖥️ GPU acceleration is used automatically if available

## 📜 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- [FaceNet-PyTorch](https://github.com/timesler/facenet-pytorch) for the MTCNN implementation
- [OpenCV](https://opencv.org/) for video processing capabilities
- [PyTorch](https://pytorch.org/) for the deep learning framework 