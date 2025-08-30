import streamlit as st
from emotion_analysis import analyze_emotion, EmotionConfig
import os

# 设置页面标题
st.title("Emotion Analysis Test")

# 创建文件上传器
video_file = st.file_uploader("Choose a video file", type=["mp4", "mov", "avi"])

# 如果文件上传成功
if video_file is not None:
    # 将视频保存到临时文件
    temp_video_path = os.path.join("temp_video.mp4")
    with open(temp_video_path, "wb") as f:
        f.write(video_file.read())

    # 设置分析配置
    config = EmotionConfig()  # 默认配置，你可以根据需要修改

    # 调用后端分析函数
    try:
        result = analyze_emotion(temp_video_path, config)
        
        # 展示结果
        st.subheader("Analysis Result")
        st.json(result)  # 显示 JSON 数据

        # 删除临时视频文件
        os.remove(temp_video_path)
    
    except Exception as e:
        st.error(f"Error: {str(e)}")
