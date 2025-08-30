import io
import json
import time
import streamlit as st
import plotly.graph_objects as go

from ui_api import get_topline_scores, get_aux_signals
from backend_api import run_full_analysis

from tabs import render_language_tab, render_visual_tab, render_raw_tab

st.set_page_config(page_title="Livestream Quality Check", layout="wide", page_icon="📹")
st.title("📹 Livestream Quality Check")
st.caption("Upload a livestream recording and get instant insights on language, visual quality, emotion, and scene content!")

left, right = st.columns([0.95, 1.05]) 

with left:
    st.subheader("⬆️ Upload & Preview")
    uploaded = st.file_uploader("Choose a video file (mp4 / mov / m4v)", type=["mp4", "mov", "m4v"])

    if uploaded:
        st.session_state["uploaded_file"] = uploaded
        size_mb = round(len(uploaded.getbuffer()) / 1024 / 1024, 2)
        st.info(f"**Filename:** {uploaded.name}　|　**Size:** {size_mb} MB", icon="📄")
        st.markdown(
            """
            <style>
            video {
                max-width: 320px !important;  /* shrink video */
                height: auto !important;
            }
            </style>
            """,
            unsafe_allow_html=True
        )
        st.video(uploaded, subtitles=None)

        st.divider()
        if st.button("Start Analysis!", use_container_width=True):
            with st.spinner("Crunching the data..."):
                # Progress styling
                st.markdown(
                    """
                    <style>
                    .stProgress > div > div > div > div {
                        background-color: #7B61FF !important;
                    }
                    </style>
                    """,
                    unsafe_allow_html=True
                )
                progress_bar = st.progress(0, text="Initializing...")

                progress_bar.progress(10, "🔍 Loading model...")
                time.sleep(0.2)

                progress_bar.progress(30, "📦 Extracting audio...")
                time.sleep(0.2)

                data = uploaded.getvalue()
                fname = uploaded.name

                def fresh_upload():
                    b = io.BytesIO(data)
                    b.name = fname
                    return b

                progress_bar.progress(60, "📝 Running transcription & core analysis...")
                results = run_full_analysis(fresh_upload()) 

                emo_result = None
                scene_result = None
                errors = {}

                progress_bar.progress(75, "💜 Running emotion analysis...")
                try:
                    from ui_api import run_emotion_from_upload  # local import to avoid early import issues
                    emo_result = run_emotion_from_upload(fresh_upload(), config=None)  # pass a fresh handle
                except Exception as e:
                    errors["emotion"] = str(e)

                progress_bar.progress(85, "🔎 Running scene (OCR/Brand) analysis...")
                try:
                    from ui_api import run_scene_analysis as run_scene_analysis_ui
                    scene_result = run_scene_analysis_ui(fresh_upload())  # pass a fresh handle
                except Exception as e:
                    errors["scene"] = str(e)

                if emo_result:
                    results["emotion"] = emo_result.get("emotion", emo_result)

                if scene_result:
                    scene_payload = scene_result.get("scene", scene_result)
                    results.setdefault("visual", {})["scene"] = scene_payload

                if errors:
                    results["errors"] = errors

                progress_bar.progress(90, "📊 Finalizing report...")
                time.sleep(0.15)

                progress_bar.progress(100, "✅ Done!")
                time.sleep(0.15)

            st.session_state["analysis"] = results
            st.success("✅ Done! Temporary files have been cleaned up.")


with right:
    st.subheader("📊 Analysis Results")

    if "analysis" not in st.session_state:
        st.info("Waiting for a video upload and analysis start on the left. ⏳")
    else:
        analysis = st.session_state["analysis"]
        lang = analysis.get("language", {}) or {}
        vis  = analysis.get("visual", {}) or {}
        meta = analysis.get("file_meta", {}) or {}

        top = get_topline_scores(lang)
        aux = get_aux_signals(lang)

        cols = st.columns(5)
        cols[0].metric("🎯 Accuracy", f"{top['accuracy']:.1f}")
        cols[1].metric("🗣️ Clarity", f"{top['clarity']:.1f}")
        cols[2].metric("📣 Persuasiveness", f"{top['persuasion']:.1f}")

        emo_score = (analysis.get("emotion") or {}).get("score")
        cols[3].metric("💜 Emotion Score", f"{float(emo_score):.1f}" if emo_score is not None else "—")

        scene_score = (vis.get("scene") or {}).get("score")
        cols[4].metric("🎬 Scene Score", f"{float(scene_score):.1f}" if scene_score is not None else "—")

        values = [
            float(top.get("accuracy", 0.0)),
            float(top.get("clarity", 0.0)),
            float(top.get("persuasion", 0.0)),
            float(emo_score or 0.0),
            float(scene_score or 0.0),
        ]
        labels = ["Accuracy", "Clarity", "Persuasion", "Emotion", "Scene"]

        values += values[:1]
        labels += labels[:1]

        radar = go.Figure(
            data=[
                go.Scatterpolar(
                    r=values,
                    theta=labels,
                    fill='toself',
                    name='Scores',
                    line=dict(color='purple'),
                    fillcolor='rgba(128, 0, 128, 0.3)',
                )
            ],
            layout=go.Layout(
                polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
                showlegend=False
            )
        )

        st.plotly_chart(radar, use_container_width=True)


        tab_lang, tab_visual, tab_raw = st.tabs(["🗣️ Language", "🎬 Visual", "🧾 Raw Data"])
        with tab_lang:
            render_language_tab(lang)

        with tab_visual:
            render_visual_tab(analysis)  # pass whole analysis (emotion + scene already inside)

        with tab_raw:
            render_raw_tab(lang, vis, meta)
