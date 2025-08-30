# Live Quality – Minimal MVP

## Setup

Create and activate a virtual environment:

```bash
python -m venv venv

# macOS / Linux
source venv/bin/activate

# Windows
venv\Scripts\activate

# install dependencies
pip install -r requirements.txt
# plus required ASR backend and utilities:
pip install faster-whisper moviepy
#install ffmpeg
ffmpeg -version

#Run
streamlit run app/main.py
