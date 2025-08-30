# app/ui_scene_demo.py
import json, streamlit as st
from scene_analysis import analyze_scene_from_upload, SceneConfig

st.title("Scene Analysis")
up = st.file_uploader("上传视频", type=["mp4","mov","mkv"])
if up and st.button("分析"):
    cfg = SceneConfig(tesseract_lang="chi_sim+eng")
    out = analyze_scene_from_upload(up, up.name, config=cfg, brand_keywords={"NIKE","耐克"})
    st.json({"scene": out["scene"]})
