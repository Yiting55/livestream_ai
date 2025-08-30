# app/ui_main.py
import json
import streamlit as st
import plotly.graph_objects as go
from ui_api import summarize_scene

from backend_api import run_full_analysis, run_scene_analysis, HAS_SCENE
from ui_api import (
    get_topline_scores, get_aux_signals,
    get_interaction_signals, get_timeline, get_highlights,
    get_compliance_score, get_flags, get_debug_info,
)

# ---------------- Page setup ----------------
st.set_page_config(page_title="Livestream Quality Check", layout="wide", page_icon="📹")
st.title("📹 Livestream Quality Check")
st.caption("Upload a livestream recording and get instant insights on language and visual performance!")

left, right = st.columns([0.95, 1.05])

# ---------------- Left: Upload & Preview ----------------
with left:
    st.subheader("⬆️ Upload & Preview")
    uploaded = st.file_uploader("Choose a video file (mp4 / mov / m4v)", type=["mp4", "mov", "m4v"])

    if uploaded:
        st.session_state["uploaded_file"] = uploaded
        size_mb = round(len(uploaded.getbuffer()) / 1024 / 1024, 2)
        st.info(f"**Filename:** {uploaded.name}　|　**Size:** {size_mb} MB", icon="📄")
        st.video(uploaded, subtitles=None)

        st.divider()
        if st.button("Start Analysis!", use_container_width=True):
            with st.spinner("Crunching the data..."):
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

                # Simulate staged loading updates
                import time
                progress_bar.progress(10, "🔍 Loading model...")
                time.sleep(0.5)

                progress_bar.progress(30, "📦 Extracting audio...")
                time.sleep(0.5)

                progress_bar.progress(60, "📝 Running transcription & analysis...")
                results = run_full_analysis(uploaded)  # Real processing happens here

                progress_bar.progress(90, "📊 Finalizing report...")
                time.sleep(0.3)

                progress_bar.progress(100, "✅ Done!")
                time.sleep(0.3)

            st.session_state["analysis"] = results
            st.success("✅ Done! Temporary files have been cleaned up.")

# ---------------- Right: Results ----------------
with right:
    st.subheader("📊 Analysis Results")

    if "analysis" not in st.session_state:
        st.info("Waiting for a video upload and analysis start on the left. ⏳")
    else:
        analysis = st.session_state["analysis"]
        lang = analysis["language"]
        vis  = analysis["visual"]
        meta = analysis["file_meta"]

        # ===== Top Cards =====
        top = get_topline_scores(lang)
        aux = get_aux_signals(lang)
        cols = st.columns(4)
        cols[0].metric("🎯 Accuracy", f"{top['accuracy']:.1f}")
        cols[1].metric("🗣️ Clarity", f"{top['clarity']:.1f}")
        cols[2].metric("📣 Persuasiveness", f"{top['persuasion']:.1f}")
        cols[3].metric("⌛ Words per Minute (WPM)", f"{aux['wpm']:.1f}")
        st.caption(f"Filler Word Rate: **{aux['filler_rate']:.3f}** (Lower is better!)")

        # ===== Radar Chart =====
        wpm_scaled = min(aux['wpm'] / 3.0, 100)
        filler_scaled = max(0, min((1 - aux['filler_rate']) * 100, 100))
        values = [top['accuracy'], top['clarity'], top['persuasion'], wpm_scaled, filler_scaled]
        labels = ["Accuracy", "Clarity", "Persuasiveness", "WPM", "Filler\n(the lower the better)"]
        values += values[:1]
        labels += labels[:1]

        fig = go.Figure(
            data=[
                go.Scatterpolar(
                    r=values,
                    theta=labels,
                    fill='toself',
                    name='Scores',
                    line=dict(color='purple'),        # Line color
                    fillcolor='rgba(128, 0, 128, 0.3)' # Fill color (transparent purple)
                )
            ],
            layout=go.Layout(
                polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
                showlegend=False
            )
        )
        st.plotly_chart(fig, use_container_width=True)

        # ===== Tabs =====
        tab_lang, tab_visual, tab_raw = st.tabs(["🗣️ Language", "🎬 Visual", "🧾 Raw Data"])

        # ---------- Language tab ----------
        with tab_lang:
            st.markdown("#### ① Interaction & Engagement")
            inter = get_interaction_signals(lang)
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("❓ Question Ratio", f"{inter['question_ratio']:.2f}")
            c2.metric("🔗 CTA Count", f"{int(inter['cta_hits'])}")
            c3.metric("💬 Reply Match Rate", f"{inter['reply_rate']:.2f}")
            c4.metric("✨ Engagement Score", f"{inter['interaction_score']:.1f}")

            st.caption("Timeline (per 10 seconds)")
            timeline = get_timeline(lang)
            if timeline:
                # Extract series
                times = [row["t"] for row in timeline]
                cta = [row.get("cta", 0) for row in timeline]
                questions = [row.get("questions", 0) for row in timeline]
                comments = [row.get("comments", 0) for row in timeline]

                # Optional: choose chart style
                style = st.segmented_control(
                    "Timeline view",
                    options=["Grouped bars", "Stacked bars", "Lines"],
                    default="Grouped bars"
                )

                fig = go.Figure()

                if style in ["Grouped bars", "Stacked bars"]:
                    fig.add_trace(go.Bar(x=times, y=cta,       name="CTAs",       marker_color="#7B61FF"))  # purple
                    fig.add_trace(go.Bar(x=times, y=questions, name="Questions",  marker_color="#8FD3FE"))  # light blue
                    fig.add_trace(go.Bar(x=times, y=comments,  name="Comments",   marker_color="#C7C9D3"))  # gray
                    fig.update_layout(barmode="group" if style == "Grouped bars" else "stack")
                else:
                    fig.add_trace(go.Scatter(x=times, y=cta,       name="CTAs",      mode="lines+markers", line=dict(color="#7B61FF")))
                    fig.add_trace(go.Scatter(x=times, y=questions, name="Questions", mode="lines+markers", line=dict(color="#8FD3FE")))
                    fig.add_trace(go.Scatter(x=times, y=comments,  name="Comments",  mode="lines+markers", line=dict(color="#C7C9D3")))

                fig.update_layout(
                    title="📊 Interaction Timeline (every 10s)",
                    xaxis_title="Time (s)",
                    yaxis_title="Count",
                    yaxis=dict(
                    tickmode="linear",  # force evenly spaced ticks
                    dtick=1,            # step = 1 (0, 1, 2, 3…)
                    rangemode="tozero"  # ensure axis always starts at 0
                ),
                legend=dict(
                    orientation="h", 
                    yanchor="bottom", y=1.02, 
                    xanchor="right", x=1
                ),
                    margin=dict(t=50, b=40, l=40, r=20),
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No timeline data to visualize yet.")
            with st.expander("📌 Highlights (Peaks in CTA & Questions)"):
                hl = get_highlights(lang)
                if hl:
                    st.json(hl)
                else:
                    st.info("No peak segments detected — interaction looks steady throughout.")

            st.markdown("#### ② Compliance & Exaggeration")
            st.metric("Compliance Score (Higher is better)", f"{get_compliance_score(lang):.1f}")
            flags = get_flags(lang)
            colA, colB = st.columns(2)
            colA.metric("Triggered Terms", str(flags["hits"]))
            colB.metric("Unique Terms", str(len(set(flags["terms"]))))
            st.write("Matched Terms:", ", ".join(flags["terms"]) or "—")
            with st.expander("Highlighted Segments"):
                highlights = flags.get("highlights", [])
            if highlights:
                st.json(highlights)
            else:
                st.info("🎉 No standout segments detected — everything looks smooth here!")

        # ---------- Visual tab ----------
        with tab_visual:
            st.markdown("#### Visual Quality Metrics")
            v = vis.get("visual_metrics") or vis.get("video") or {}
            if not v:
                st.info("No visual metrics available yet — waiting on video-side processing.", icon="🧩")
            else:
                v1, v2, v3, v4 = st.columns(4)
                v1.metric("✂️ Scene Cuts", f"{v.get('cuts', 0)}")
                v2.metric("📉 Shake Variance", f"{v.get('shake_var', 0.0):.3f}")
                v3.metric("🌞 Overexposure %", f"{v.get('over_exposure_ratio', 0.0):.3f}")
                v4.metric("📦 Product Visibility", f"{v.get('product_visibility', 0.0):.3f}")
                st.caption("Brightness Stats")
                vv1, vv2 = st.columns(2)
                vv1.metric("Avg Brightness", f"{v.get('brightness_mean', 0.0):.3f}")
                vv2.metric("Brightness StdDev", f"{v.get('brightness_std', 0.0):.3f}")

            st.divider()
            st.markdown("#### Scene Analysis (OCR / Brand Detection)")
            if not HAS_SCENE:
                st.info("Scene analysis module not found.")
            else:
                up = st.session_state.get("uploaded_file")
                c1, c2 = st.columns([1, 2])
                with c1:
                    tess_lang = st.text_input("Tesseract OCR Language", value="chi_sim+eng")
                with c2:
                    kw_str = st.text_input("Brand Keywords (comma-separated)", value="NIKE, 耐克")
                brand_keywords = {k.strip() for k in kw_str.split(",") if k.strip()}
                if st.button("🔍 Run Scene Analysis", disabled=up is None, use_container_width=True):
                    with st.spinner("🔎 Analyzing scene content..."):
                        out = run_scene_analysis(up, tess_lang, brand_keywords)
                        scene = out.get("scene", {})
                        summary_md, moments = summarize_scene(scene)

                        st.markdown(summary_md)

                        st.markdown("### OCR / Brand Moments")
                        if moments:
                            for m in moments:
                                if m["start_s"] == m["end_s"]:
                                    st.write(f"- **{m['type']}** at **t={m['start_s']}s**")
                                else:
                                    st.write(f"- **{m['type']}** from **t={m['start_s']}s** to **t={m['end_s']}s**")
                        else:
                            st.caption("No OCR or brand moments to show.")


        # ---------- Raw tab ----------
        with tab_raw:
            st.markdown("#### Export Full Report")
            export_all = {"language": lang, "visual": vis}
            json_bytes = json.dumps(export_all, ensure_ascii=False, indent=2).encode("utf-8")
            st.download_button(
                "💾 Download Full JSON",
                data=json_bytes,
                file_name=(meta.get("name", "analysis") + ".json"),
                mime="application/json",
            )

            st.markdown("#### Debug Info")
            with st.expander("debug", expanded=False):
                st.json(get_debug_info(lang))
