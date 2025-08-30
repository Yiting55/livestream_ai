# app/tabs.py
from __future__ import annotations
from typing import Dict, Any, List
import json
import streamlit as st
import plotly.graph_objects as go

from ui_api import (
    get_interaction_signals, get_timeline, get_highlights,
    get_compliance_score, get_flags, get_debug_info,
    build_emotion_chart,
    summarize_scene,
)

# ---------- Language tab ----------
def render_language_tab(lang: Dict[str, Any]) -> None:
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

        style = st.segmented_control(
            "Timeline view",
            options=["Grouped bars", "Stacked bars", "Lines"],
            default="Grouped bars"
        )

        fig = go.Figure()
        if style in ["Grouped bars", "Stacked bars"]:
            fig.add_trace(go.Bar(x=times, y=cta,       name="CTAs",       marker_color="#7B61FF"))
            fig.add_trace(go.Bar(x=times, y=questions, name="Questions",  marker_color="#8FD3FE"))
            fig.add_trace(go.Bar(x=times, y=comments,  name="Comments",   marker_color="#C7C9D3"))
            fig.update_layout(barmode="group" if style == "Grouped bars" else "stack")
        else:
            fig.add_trace(go.Scatter(x=times, y=cta,       name="CTAs",      mode="lines+markers", line=dict(color="#7B61FF")))
            fig.add_trace(go.Scatter(x=times, y=questions, name="Questions", mode="lines+markers", line=dict(color="#8FD3FE")))
            fig.add_trace(go.Scatter(x=times, y=comments,  name="Comments",  mode="lines+markers", line=dict(color="#C7C9D3")))

        fig.update_layout(
            title="📊 Interaction Timeline (every 10s)",
            xaxis_title="Time (s)",
            yaxis_title="Count",
            yaxis=dict(tickmode="linear", dtick=1, rangemode="tozero"),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
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
def render_visual_tab(analysis: Dict[str, Any]) -> None:
    vis = analysis.get("visual", {}) or {}
    emo = analysis.get("emotion", None)
    err = (analysis.get("errors") or {}).copy()

    # ---- Emotion
    st.divider()
    st.markdown("#### 💜 Emotion Analysis (Faces/Voice)")
    if "emotion" in err:
        st.error(f"Emotion analysis failed: {err['emotion']}")
    elif emo:
        try:
            fig_emo = build_emotion_chart(analysis)  # accepts {"emotion": {...}} or root dict
            st.plotly_chart(fig_emo, use_container_width=True)
            with st.expander("Raw Emotion JSON"):
                st.json(analysis.get("emotion"))
        except Exception as e:
            st.error(f"Failed to render emotion chart: {e}")
    else:
        st.info("Emotion results not available in this run.")

    # ---- Scene
    st.divider()
    st.markdown("#### Scene Analysis (OCR / Brand Detection)")
    scene = vis.get("scene") or {}
    if "scene" in err:
        st.error(f"Scene analysis failed: {err['scene']}")
    elif scene:
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
    else:
        st.info("Scene analysis results not available in this run.")


# ---------- Raw tab ----------
def render_raw_tab(lang: Dict[str, Any], vis: Dict[str, Any], meta: Dict[str, Any]) -> None:
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
