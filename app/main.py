import os
import streamlit as st
from analyzer import analyze_video
from io_utils import save_upload_to_tempfile, remove_path

st.set_page_config(page_title="直播录屏 · 上传预览 & 分析", layout="wide")
st.title("📹 带货直播：上传与预览（左）｜分析结果（右）")

left, right = st.columns(2)

with left:
    st.subheader("左侧：上传 & 预览")
    uploaded = st.file_uploader("选择视频（mp4/mov/m4v）", type=["mp4", "mov", "m4v"])
    if uploaded:
        size_mb = round(len(uploaded.getbuffer()) / 1024 / 1024, 2)
        st.caption(f"文件：{uploaded.name} · 大小：{size_mb} MB")
        # 直接在线预览（不落盘）
        st.video(uploaded)

        if st.button("开始分析（保存到临时目录 → 分析后自动删除）", use_container_width=True):
            # 1) 保存到临时文件
            tmp_path, tmp_dir = save_upload_to_tempfile(uploaded, show_progress=True)

            # 2) 调用分析（此处可逐步扩展更多维度/ASR/NLP）
            with st.spinner("分析中…"):
                result = analyze_video(tmp_path)

            # 3) 立刻删除临时文件/目录
            remove_path(tmp_dir)

            # 4) 存结果到会话态，给右侧展示
            st.session_state["analysis"] = result
            st.success("分析完成（临时文件已清理）")

with right:
    st.subheader("右侧：分析结果")
    if "analysis" not in st.session_state:
        st.info("等待左侧上传并点击“开始分析”。")
    else:
        res = st.session_state["analysis"]
        # 基础指标（占位：亮度）
        st.metric("平均亮度", f"{res['avg_brightness']:.1f} / 255")
        st.metric("亮度评分（示例）", f"{res['brightness_score']:.1f} / 100")
        st.caption("说明：当前仅展示亮度占位指标；后续会加入互动性/话术/真实性/专业性/画面氛围等维度。")

        # 价值分享（示例）：用亮度评分充当总分 Q 的替身
        q = float(res["brightness_score"])
        if q >= 80: mult = 1.2
        elif q >= 60: mult = 1.0
        elif q >= 40: mult = 0.8
        else: mult = 0.6
        base_pool = 100
        st.write(f"**价值分享示意**：基础池 {base_pool} × 质量乘数 {mult} = **{base_pool * mult:.1f}**")
        st.caption("最终会改为：基础池 × 质量乘数(Q) × 互动乘数(评论密度)。")
