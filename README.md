# 🎥 **Livestream Quality Analysis**

A **Streamlit-based application** for analyzing and scoring livestream shopping videos.  
It evaluates **language quality (ASR + NLP)**, **visual scene quality (OpenCV + OCR)**, and **presenter emotion engagement (facial cues + speech)** to generate a **multi-dimensional livestream scorecard**.

---

## ✨ **Overview**

The **Livestream Quality Analysis System** is an automated tool designed to provide comprehensive insights into livestream content. It combines Automatic Speech Recognition (ASR), Natural Language Processing (NLP), computer vision, and emotion analysis to produce an objective, transparent scorecard for livestreams. The system evaluates multiple dimensions such as **engagement**, **clarity**, **persuasion**, **compliance**, **scene quality**, and **emotion** to help content creators, reviewers, and brands ensure their livestreams are effective, engaging, and aligned with brand standards.

---

## ✨ **Features**

- **Video Upload & Preview**: Upload `.mp4` / `.mov` videos directly in the browser for real-time analysis and preview.
  
- **Automated Analysis**:
  - **Language Analysis**:
    - Accuracy (evidence-based claims)
    - Clarity (speech rate, filler words)
    - Persuasion (CTA and urgency usage)
    - Interaction & pacing (questions, CTAs, replies, timeline)
    - Compliance (exaggeration / risky terms)
  - **Scene Analysis**:
    - Brightness, saturation, contrast, sharpness
    - OCR text extraction (on-screen content)
    - Logo/brand detection for compliance
  - **Emotion Analysis**:
    - Valence (positivity of facial expressions)
    - Energy (presenter engagement via movement and speech)

- **Visualizations**:
  - Metrics, radar charts, timelines, highlights, and tag clouds for analysis.

- **Export**:
  - Download structured JSON reports (optional PDF/structured reports).

- **Temp File Management**:
  - Uploaded files are auto-deleted after analysis for better efficiency.

---

## 🚧 **Challenges Addressed**

The rapid growth of **livestream e-commerce** presents several challenges:
1. **Ensuring Engagement**: Hosts must use effective CTAs, respond to audience questions, and maintain an interactive environment.
2. **Maintaining Clarity**: Speech must be fluent, well-paced, and free from excessive filler words.
3. **Demonstrating Persuasion**: Livestream hosts must employ urgency and effective language to drive sales.
4. **Guaranteeing Compliance**: Exaggerated claims, misleading statements, and violation of brand guidelines must be detected and flagged.
5. **Monitoring Visual Quality**: The video quality must meet certain standards, and brand logos should be properly displayed.

This tool provides automated solutions for assessing all these aspects using a combination of **ASR**, **NLP**, and **computer vision** technologies.

---

## 🔮 **What's Next for the Project?**

Future improvements include:
- **Extended Scene Analysis**: More advanced object detection for identifying products and brands in livestreams.
- **AI-Powered Recommendations**: Using the analysis to provide actionable suggestions for improving livestream quality.
- **Real-Time Analysis**: Incorporating streaming capabilities to analyze livestreams as they are being broadcast.
- **Enhanced Emotion Analysis**: Deepening emotion recognition by analyzing a broader range of facial expressions and vocal tones.

---

## ⚙️ **Tech Stack**

- **Python**: The primary programming language.
- **Streamlit**: Interactive UI framework for real-time, in-browser analysis.
- **faster-whisper / openai-whisper**: ASR tools for speech recognition.
- **OpenCV**: Video frame analysis, including brightness, contrast, and sharpness.
- **Tesseract OCR**: For scene text extraction and brand logo detection.
- **MediaPipe**: Facial expression and engagement analysis.
- **MoviePy**: Video/audio extraction and processing.
- **Plotly / Matplotlib**: Data visualization tools for charts and timelines.
- **NumPy / Pandas**: Data handling for scoring and analysis.
- **reportlab (optional)**: PDF report generation.

---

## 🚩 **Problem Statement**

Livestream e-commerce is growing rapidly, but there are few tools to objectively evaluate the quality and compliance of livestream content. This project addresses that gap by providing an automated, multi-dimensional analysis of livestream videos, helping sellers, brands, and platforms improve content engagement and ensure compliance with brand standards.

---

## 🛠️ **Setup**

### 1. Clone the repository
```bash
git clone https://github.com/Yiting55/livestream_ai.git
cd livestream_ai
```

### 2. Create and activate a virtual environment
```bash
python3.11.9 -m venv venv
```
#macOS / Linux
```bash
source venv/bin/activate
```
#Windows
```bash
venv\Scripts\activate
```
### 3. Install dependencies
```bash
pip install -r requirements.txt
```
### 4. Install ASR backend and utilities
```bash
pip install faster-whisper moviepy
```
### 5. Install ffmpeg
```bash
ffmpeg -version
```
### 6. Install Tesseract OCR
#macOS / Linux
```bash
brew install tesseract
```
#Windows
```bash
scoop install tesseract
```
### 7. Run the application
```bash
streamlit run app/main.py
```
