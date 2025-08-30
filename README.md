# 🎥 Live Quality Analysis

A **Streamlit-based application** for analyzing and scoring livestream shopping videos.  
It evaluates **language quality (ASR + NLP)**, **visual scene quality (OpenCV + OCR)**, and **presenter emotion engagement (facial cues + speech)** to generate a **multi-dimensional livestream scorecard**.  

---

## ✨ Features
- **Video Upload & Preview**: Upload `.mp4` / `.mov` videos directly in browser.  
- **Language Analysis**:
  - Accuracy (evidence-based claims)  
  - Clarity (speech rate, filler words)  
  - Persuasion (CTA and urgency usage)  
  - Interaction & pacing (questions, CTAs, replies, timeline)  
  - Compliance (exaggeration / risky terms)  
- **Scene Analysis** *(optional)*:
  - Brightness, saturation, contrast, sharpness  
  - OCR text extraction (on-screen content)  
  - Logo/brand detection for compliance  
- **Emotion Analysis** *(optional)*:
  - Valence (positivity of facial expressions)  
  - Energy (presenter engagement via movement and speech)  
- **Visualization**:
  - Metrics, radar charts, timelines, highlights, tag clouds  
- **Export**: Download structured JSON reports (with optional PDF reports)  
- **Temp File Management**: Uploaded files auto-deleted after analysis  

---

## ⚙️ Setup

### 1. Clone the repository
git clone https://github.com/Yiting55/livestream_ai.git
cd livestream_ai

### 2. Create and activate virtual environment
python -m venv venv

# macOS / Linux
source venv/bin/activate

# Windows
venv\Scripts\activate

### 3. Install dependencies
pip install -r requirements.txt

### 4. Install ASR backend and utilities
pip install faster-whisper moviepy

### 5. Install ffmpeg
ffmpeg -version

### 6. Install Tesseract OCR (for Scene Analysis, optional)
# macOS
brew install tesseract

# Windows (with Scoop)
scoop install tesseract

### 7. Run the application
streamlit run app/main.py

##📚Tech Stack

Python 3.9+ / 3.10+
Streamlit – interactive UI framework
faster-whisper / openai-whisper – ASR (speech recognition)
OpenCV – video frame processing (brightness, saturation)
Tesseract OCR – brand/logo detection
MediaPipe – facial expression / emotion analysis
MoviePy – audio extraction & frame handling
Plotly – visualization (charts, timelines, radar)
NumPy / Pandas – data processing

##🚩 Problem Addressed
Livestream e-commerce is expanding rapidly, but quality and compliance vary greatly.
This project provides an automated, objective scoring system to evaluate livestreams across multiple dimensions:
- Engagement (questions, CTAs, replies)
- Clarity (speech pace, filler words)
- Persuasion (CTA effectiveness, urgency framing)
- Compliance (avoid exaggerated claims)
- Visual quality (brightness, saturation, logos)
- Emotion (positivity and energy)
It enables sellers, reviewers, and brands to ensure livestreams are engaging, compliant, and effective.

##📤 Output

The app produces structured results containing:
Scores (Accuracy, Clarity, Persuasion, Compliance, Interaction, Scene, Emotion)
Signals (WPM, filler rate, CTA hits, reply rate, exaggeration terms)
Visualisation charts
