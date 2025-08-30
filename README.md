# 🎥 **Content Creation & Reward Mechanism Evaluation System**

A **Streamlit-based application** designed to analyze and score content creation performance on platforms like TikTok, focusing on key factors for designing fair and effective reward mechanisms. The system evaluates **content quality**, **profit-sharing mechanisms**, and **compliance** to ensure a transparent and legitimate flow of value from consumers to creators.

---

## ✨ **Overview**

This tool aims to design a fair and effective value-sharing solution for content creators, with a focus on short-form video and livestream platforms like TikTok. By evaluating **content quality**, **audience engagement**, and **regulatory compliance**, the system helps ensure that creators are fairly compensated based on their performance, and that mechanisms like **profit-sharing**, **AML compliance**, and **anti-fraud prevention** are integrated into the platform.

The application combines **content quality evaluation**, **audience interaction analysis**, **compliance checks**, and **bonus point systems** to help platforms and creators build a more transparent, equitable ecosystem.

---

## ✨ **Features**

- **Content Quality Assessment**: Analyze video content quality to ensure it aligns with platform standards for fair rewards.
  
- **Audience Interaction**: Evaluate the level of engagement (likes, comments, shares) to assess the content's effectiveness in connecting with viewers.

- **Profit-Sharing Mechanism**: Design a transparent model to calculate how rewards are distributed based on content performance and engagement.

- **AML & Compliance Checks**: Automatically detect and flag potential compliance issues and fraudulent activity (such as system gaming or manipulation of engagement metrics).

- **Fraud Prevention**: Use advanced algorithms to ensure creators' performance metrics are accurate and immune to manipulation.

- **Bonus Points 🌟**: A system to reward exceptional creators with bonus points based on performance, audience interaction, and content impact.

- **Transparency and Reporting**: Provide detailed reports on content performance, compliance, and reward calculations.

---

## 🚧 **Challenges Addressed**

As TikTok and similar platforms grow, ensuring fair rewards and a transparent value exchange becomes increasingly complex. Key challenges include:
1. **Fair Reward Distribution**: How can creators be compensated fairly based on the value they provide to consumers?
2. **Regulatory Compliance**: How can platforms ensure that creators' earnings comply with regulations, including **AML** and other legal requirements?
3. **Fraud Prevention**: How can the system prevent creators from gaming the system (e.g., by artificially inflating engagement metrics)?
4. **Content Quality Evaluation**: How can the system accurately assess the quality of the content and the creator's contribution to platform value?
5. **Bonus Point Allocation**: How can creators receive bonus rewards based on exceptional content quality and audience interaction?

This tool is designed to provide data-driven insights for a **transparent value-sharing system**, helping platforms like TikTok ensure fairness, compliance, and fraud prevention in their reward mechanisms.

---

## 🔮 **What's Next for the Project?**

Future developments will include:
- **Dynamic Profit-Sharing Models**: Implement machine learning to optimize reward distribution dynamically based on content performance, audience feedback, and creator contribution.
- **Advanced Fraud Detection**: Enhance the system’s fraud detection capabilities using AI to detect suspicious behavior in content engagement metrics.
- **Real-Time Analytics**: Build a real-time analysis tool for live streams to ensure creators' performance is continually evaluated and rewarded during broadcasts.
- **Regulatory Monitoring**: Integrate more compliance features, especially regarding **AML** regulations and jurisdictional requirements for global platforms.
- **Bonus Point Mechanism Expansion**: Introduce more sophisticated bonus systems, rewarding creators based on a combination of factors like video quality, audience retention, and content impact.

---

## ⚙️ **Tech Stack**

- **Python**: Primary programming language for backend logic.
- **Streamlit**: Interactive framework for building the user interface.
- **faster-whisper / openai-whisper**: ASR tools for speech-to-text processing in video content.
- **OpenCV**: Video processing for quality assessment, including brightness, contrast, and sharpness.
- **MediaPipe**: Analyzes facial expressions and audience interaction for emotion detection.
- **MoviePy**: Handles video/audio extraction and processing.
- **Plotly / Matplotlib**: Used for visualizing key metrics, engagement timelines, and reward distributions.
- **NumPy / Pandas**: For data handling, especially regarding performance metrics and reward calculations.
- **reportlab (optional)**: PDF report generation for detailed content and performance reports.

---

## 🚩 **Problem Statement**

As TikTok and similar platforms grow, content creators face challenges in ensuring fair compensation based on the value they provide. This project addresses the need for an automated, transparent reward system by evaluating key factors such as content quality, audience engagement, compliance with regulations, and fraud prevention. 

Key issues to address include:
- **Ensuring Fair Compensation**: Fairly distribute rewards based on content performance and engagement metrics.
- **Regulatory Compliance**: Implement systems to monitor and enforce AML compliance and fraud prevention.
- **Fraud and System Gaming Prevention**: Use advanced techniques to ensure performance metrics remain authentic and unmanipulated.
- **Bonus Point Rewards**: Reward creators with bonus points for exceptional performance and engagement.

This system helps create a more equitable content creation ecosystem, promoting **transparency**, **compliance**, and **fair value exchange** between creators and consumers.

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
