# 🎥 **Livestream Quality & Reward Evaluation System**

A **Streamlit-based application** designed to evaluate content quality, audience engagement, and compliance for platforms like TikTok, with the ultimate goal of supporting a **fair and transparent reward mechanism**. The system evaluates **content quality**, **audience interaction**, and **compliance checks** to ensure that creators are compensated based on their contributions and engagement.

---

## ✨ **Overview**

This tool provides a **multi-dimensional** analysis of livestreams and videos, aiming to align with the goals of designing a fair reward mechanism for content creators. The application evaluates key factors such as **content quality**, **audience engagement**, **compliance with regulations**, and **fraud prevention**, addressing the core challenges faced by platforms like TikTok. While the current functionality does not directly implement reward mechanisms, the system provides a foundation for evaluating performance and ensuring compliance, which are key to designing a transparent value-sharing system.

---

## ✨ **Features**

### **1. Video Upload & Preview**
- **Upload and preview videos** directly in the browser, supporting `.mp4` and `.mov` formats.
- Real-time processing allows creators to quickly see their content's performance metrics.

### **2. Automated Analysis**

#### **Language Analysis**
- **Accuracy**: Measures how well the content adheres to evidence-based claims to avoid misinformation.
- **Clarity**:
  - **Speech Rate (WPM)**: Evaluates the speed at which the presenter speaks.
  - **Filler Words**: Analyzes the use of filler words like "um" and "uh" to assess speech fluency.
- **Persuasion**:
  - **CTA Usage**: Tracks the frequency of Calls to Action (CTAs) used by the presenter.
  - **Urgency Framing**: Identifies usage of urgency or scarcity terms (e.g., "limited time only").
- **Interaction & Pacing**:
  - **Questions**: Measures how many questions are asked to the audience.
  - **Replies to Comments**: Analyzes how actively the creator engages with audience comments.
  - **CTA Response Rate**: Evaluates how effectively the audience responds to CTAs.
- **Compliance**:
  - **Exaggerated Claims**: Detects the use of exaggerated or misleading language (e.g., "100% guaranteed").
  - **Risky Terms**: Flags sensitive or misleading terms that may violate platform rules.

#### **Scene Analysis**
- **Brightness, Saturation, Contrast, Sharpness**: Assesses visual quality of the video to ensure it meets platform standards.
- **OCR Text Extraction**: Detects and extracts any on-screen text (e.g., product names, logos).
- **Logo/Brand Detection**: Identifies logos and checks for brand compliance, ensuring the content adheres to brand guidelines.

#### **Emotion Analysis**
- **Valence**: Analyzes the emotional positivity of the presenter by detecting facial expressions (e.g., smiles, frowns).
- **Energy**: Measures the presenter's engagement through movement and speech analysis, helping assess the level of enthusiasm or energy in the presentation.

### **3. Visualizations**
- **Metrics and Radar Charts**: Visualize content scores across multiple dimensions such as language, interaction, and emotion.
- **Timelines and Highlights**: Display content timestamps where key events or metrics (e.g., high engagement or compliance issues) occurred.
- **Tag Clouds**: Show frequently mentioned terms and key phrases in the content.

### **4. Export**
- **Downloadable JSON Reports**: Export detailed performance data in a structured format for further analysis.
- **Optional PDF/Structured Reports**: Generate formal reports containing key insights, useful for sharing with stakeholders.

### **5. Temp File Management**
- **Efficient File Handling**: Uploaded files are automatically deleted after analysis, ensuring efficient use of storage and protecting user privacy.

---

## 🚧 **Challenges Addressed**

While the system does not yet implement a full reward mechanism, it directly supports the design of a transparent value-sharing model by addressing several challenges:

1. **Content Quality Evaluation**: Analyzing content clarity, accuracy, and persuasion through **ASR** and **NLP** to determine if the content meets the required standards for fair compensation.
  
2. **Audience Interaction**: Ensuring that creators are rewarded based on engagement metrics such as CTAs, questions, and replies.

3. **Compliance**: Detecting problematic content by flagging **exaggeration** or **misleading claims**, ensuring creators adhere to platform regulations.

4. **Fraud Prevention**: Ensuring that the performance metrics are legitimate and immune to manipulation, such as artificially inflating engagement or metrics.

5. **Bonus Point System**: Rewarding creators with bonus points based on the quality and impact of their content, which can serve as a foundation for future reward structures.

---


## ⚙️ **Tech Stack**

- **Python**: Primary programming language for backend analysis.
- **Streamlit**: Interactive UI framework for real-time, in-browser content evaluation.
- **faster-whisper / openai-whisper**: ASR tools for transcription and content analysis.
- **OpenCV**: Video frame analysis for assessing visual quality and detecting compliance issues.
- **MediaPipe**: Facial expression and emotion analysis for engagement detection.
- **MoviePy**: Video/audio extraction for content analysis.
- **Plotly / Matplotlib**: For visualizing key metrics like content quality and engagement.
- **NumPy / Pandas**: Data handling for performance metrics and scoring.
- **reportlab (optional)**: PDF report generation for downloadable content analysis reports.

---

## 🚩 **Problem Statement**

TikTok-like platforms face challenges in ensuring that **content creators** are compensated fairly, based on the quality of their content and the level of audience engagement. However, designing an automated reward mechanism that incorporates **fairness**, **compliance**, and **fraud prevention** is a complex task. This system provides a solution by evaluating key content factors, such as **clarity**, **engagement**, and **compliance**. These insights can be used as the foundation for building transparent and fair reward mechanisms for creators.

The system does not yet handle **profit distribution** directly, but it creates a pathway for transparent evaluation, which is crucial for designing a legitimate value-sharing system for creators.

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
