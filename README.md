# Live Quality – Minimal MVP

## Setup
python -m venv venv
# mac/linux
source venv/bin/activate
# windows
venv\Scripts\activate
pip install -r requirements.txt

## Run
streamlit run app/main.py

## Notes
- 上传后可直接预览（不落盘）。
- 点击“开始分析”时才写到系统临时目录，分析结束即自动删除。
- 如需更大上传，在项目根建 .streamlit/config.toml：
  [server]
  maxUploadSize = 1024
