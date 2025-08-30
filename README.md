# 🎥 **StreamWise - Livestream Quality & Reward Evaluation System**

StreamWise is a **Streamlit-based application** designed to evaluate the quality, engagement, and compliance of live streams, particularly for eCommerce platforms like TikTok. Its ultimate goal is to support a **fair and transparent reward mechanism**, ensuring that content creators are compensated based on their actual contributions and engagement.



##  **Inspiration**

With the rapid rise of eCommerce live streaming, many viewers experience frustration with low-quality, unengaging broadcasts. Streamers often lack energy, leading to a poor user experience. We wanted to create a solution that not only helps viewers find high-quality content but also empowers creators to improve. The goal was to build a platform that quantifies livestream quality, promotes transparency, and enhances the user experience, ultimately contributing to a better reward system for creators.



##  **Features**

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



##  **Challenges we ran into**

- **Unfamiliarity with Video Analysis**: Working with video content was a new area for our team, and it required significant time to explore and learn the tools and techniques for accurate video analysis.
- **Finding Quality Test Videos**: It was challenging to find a variety of test videos that effectively demonstrated differences in content quality, which made it difficult to fine-tune the system.



##  **Accomplishments that we're proud of**

- **Team Collaboration**: Despite the challenges of working during the semester, our team maintained strong communication, aligned on key details early, and kept an open line of discussion throughout the process.
- **Working Web App**: We successfully built a functioning web app that enables video analysis, contributing to the reimagination of a transparent and effective reward system for eCommerce live streaming.
- **Deeper Understanding**: Our project gave us a much clearer understanding of the critical elements that define high-quality eCommerce live streams, such as audience engagement, energy levels, and presentation clarity.



##  **What we learned**

- **Critical Elements of a High-Quality Stream**: We learned the importance of factors like presenter energy, pacing, and audience interaction in determining the success of a live stream.
- **Dynamic Nature of Live Content**: We gained a deeper understanding of how live stream content needs to be dynamic and responsive to keep the audience engaged, rather than static.
- **Tech Integration**: Integrating various analysis tools like speech-to-text, emotion recognition, and video quality assessment required us to better understand how these components can seamlessly work together to enhance the user experience.



##  **What's next for StreamWise**

- **Faster Processing for Longer Videos**: Currently, the system can only process shorter videos, and longer videos take more time to analyze. Improving the processing speed for longer videos is a priority for future updates.
- **Enhanced Visualizations**: We plan to improve the visual representation of each quality criterion, providing users with clearer, more actionable insights into the strengths and weaknesses of their streams.
- **AI-Driven Recommendations**: Moving beyond simple scores, we aim to build AI-driven recommendations that offer personalized advice to creators, helping them improve specific aspects of their live streams.

##  **Tech Stack**

We built StreamWise using **Streamlit** for the interactive frontend, ensuring an easy-to-use interface for real-time analysis. For backend processing:

- **faster-whisper** was integrated for speech-to-text analysis, converting live stream audio into text.
- **OpenCV** was used to assess video quality (brightness, contrast, sharpness, etc.).
- **MediaPipe** provided emotion analysis to measure the presenter's engagement and enthusiasm.
- **Tesseract OCR** was used to extract on-screen text, improving brand detection and content accuracy.
- **MoviePy** was used for video/audio extraction, enabling in-depth content analysis.

We also utilized **Python** libraries like **Pandas** and **NumPy** for data processing and analysis. For visualizing key metrics like content quality and engagement, we used **Plotly** and **Matplotlib** to create intuitive and interactive charts.


##  **Problem Statement**

TikTok-like platforms face challenges in ensuring that **content creators** are compensated fairly, based on the quality of their content and the level of audience engagement. However, designing an automated reward mechanism that incorporates **fairness**, **compliance**, and **fraud prevention** is a complex task. This system provides a solution by evaluating key content factors, such as **clarity**, **engagement**, and **compliance**. These insights can be used as the foundation for building transparent and fair reward mechanisms for creators.

The system does not yet handle **profit distribution** directly, but it creates a pathway for transparent evaluation, which is crucial for designing a legitimate value-sharing system for creators.


##  **Setup**

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
pip install faster-whisper moviepy mediapipe
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
