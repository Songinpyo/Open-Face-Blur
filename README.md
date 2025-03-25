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

### Requirements

- Python 3.8
- Conda package manager

### Dependencies

- PyTorch 1.13.1
- torchvision 0.14.1
- facenet-pytorch 2.5.2
- opencv-python 4.7.0
- pillow 9.4.0
- numpy 1.24.1

### Step 1: Clone the repository or download the source code

```bash
git clone https://github.com/yourusername/face-blur-framework.git
cd face-blur-framework
```

### Step 2: Create and activate a Conda environment

```bash
# Create a new Conda environment named "faceblur" with Python 3.8
conda create -n faceblur python=3.8
conda activate faceblur
```

### Step 3: Install dependencies with Conda and pip

```bash
# Install PyTorch, torchvision
pip install torch==1.13.1 torchvision==0.14.1

# Install remaining dependencies through pip
pip install facenet-pytorch==2.5.2
pip install opencv-python==4.7.0.72
pip install pillow==9.4.0
pip install numpy==1.24.1
```

### Alternative Install for CPU-Only (no GPU)

```bash
# Install CPU-only PyTorch
conda install pytorch=1.13.1 torchvision=0.14.1 cpuonly -c pytorch
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
| A / Left  | ⏮️ Previous frame                         |
| D / Right | ⏭️ Next frame                            |
| F         | 📋 Copy regions to next frame & move forward |
| Q         | 🔄 Toggle auto-detect faces mode (on/off) |
| R         | 🔍 Run face detection on current frame    |

## 🔮 Future Development Plans

- [ ] Adjustable Bounding Boxes — Interactive drag functionality to resize and reposition blur regions for more precise control  
- [ ] Advanced Face Detection Models — Integration of newer, more accurate face detection architectures to improve detection rate and reduce false positives  

## 📜 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- [FaceNet-PyTorch](https://github.com/timesler/facenet-pytorch) for the MTCNN implementation
- [OpenCV](https://opencv.org/) for video processing capabilities
- [PyTorch](https://pytorch.org/) for the deep learning framework 