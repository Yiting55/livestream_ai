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

# main.py (only touch the "right" panel section)
# app/main.py（右侧展示区替换）
with right:
    st.subheader("右侧：分析结果")
    if "analysis" not in st.session_state:
        st.info("等待左侧上传并点击“开始分析”。")
    else:
        res = st.session_state["analysis"]

        st.markdown("### 🗣️ Language (EN) – Mini Scores")
        ls = res.get("lang_scores") or {}
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.metric("Accuracy/Compliance", f"{ls.get('accuracy', 0):.1f}")
        with c2:
            st.metric("Clarity", f"{ls.get('clarity', 0):.1f}")
        with c3:
            st.metric("Persuasion (CTA)", f"{ls.get('persuasion', 0):.1f}")
        with c4:
            st.metric("WPM", f"{ls.get('wpm', 0):.1f}")
        st.caption(f"Filler rate: {ls.get('filler_rate', 0.0)} (lower is better)")

        st.markdown("#### Interaction & Pacing")
        inter = res.get("lang_interaction") or {}
        colA, colB, colC = st.columns(3)
        sig = inter.get("signals") or {}
        with colA: st.metric("Question Ratio", str(sig.get("question_ratio", 0.0)))
        with colB: st.metric("CTA Hits", str(sig.get("cta_hits", 0)))
        with colC: st.metric("Reply Rate", str(sig.get("reply_rate", 0.0)))
        st.caption("Timeline per 10s window")
        st.dataframe(inter.get("timeline") or [])

        st.markdown("#### Exaggeration / Compliance")
        ex = res.get("lang_exaggeration") or {}
        st.write("Hits:", (ex.get("signals") or {}).get("exaggeration_hits", 0))
        st.write("Terms:", (ex.get("signals") or {}).get("terms", []))
        with st.expander("Highlights"):
            st.json(ex.get("highlights") or [])
