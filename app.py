"""
@file app.py
@description Streamlit interactive diagnostic frontend with span highlighting, model selection, real-time patching, and stylometry
@module orto/ui
"""

import html
import os
import streamlit as st

from orto.core.linguistic_fallback import UniversalLinguisticEngine
from orto.core.patcher import ReverseOffsetPatcher
from orto.core.syntax_engine import SyntaxEngine
from orto.critic.verifier import SymbolicCritic
from orto.llm.client import LLMClient
from orto.pipeline import OrtoEngine
from orto.style.analyzer import StyleAnalyzer
from orto.style.naturalizer import StyleNaturalizer

st.set_page_config(
    page_title="Orto | Neurosymbolic GEC & Diagnostic Engine",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS for rich typography, badge pills, and glassmorphic diagnostic cards
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap');

    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }
    code, pre {
        font-family: 'JetBrains Mono', monospace !important;
    }
    .main-title {
        font-size: 2.2rem;
        font-weight: 800;
        background: linear-gradient(135deg, #6366F1 0%, #A855F7 50%, #EC4899 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.2rem;
    }
    .subtitle {
        color: #94A3B8;
        font-size: 1.05rem;
        margin-bottom: 1.5rem;
    }
    .badge-spell { background: #8B5CF622; color: #A78BFA; border: 1px solid #8B5CF666; }
    .badge-sva { background: #EF444422; color: #F87171; border: 1px solid #EF444466; }
    .badge-tense { background: #F9731622; color: #FB923C; border: 1px solid #F9731666; }
    .badge-noun { background: #3B82F622; color: #60A5FA; border: 1px solid #3B82F666; }
    .badge-prep { background: #10B98122; color: #34D399; border: 1px solid #10B98166; }
    .badge-det { background: #F59E0B22; color: #FBBF24; border: 1px solid #F59E0B66; }
    .badge-wo { background: #6366F122; color: #818CF8; border: 1px solid #6366F166; }
    .badge-other { background: #64748B22; color: #94A3B8; border: 1px solid #64748B66; }

    .errant-pill {
        display: inline-block;
        padding: 0.2rem 0.6rem;
        border-radius: 9999px;
        font-size: 0.8rem;
        font-weight: 700;
        letter-spacing: 0.05em;
        text-transform: uppercase;
        margin-right: 0.4rem;
    }
    .tier-badge {
        display: inline-block;
        padding: 0.3rem 0.8rem;
        border-radius: 6px;
        font-size: 0.85rem;
        font-weight: 600;
        background: #1E1B4B;
        color: #A5B4FC;
        border: 1px solid #6366F188;
        margin-bottom: 0.8rem;
    }
    .highlight-span {
        padding: 0.15rem 0.4rem;
        border-radius: 4px;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.2s ease;
    }
    .highlight-span:hover {
        filter: brightness(1.2);
    }
    .card {
        background: #1E293B33;
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 1.2rem;
        margin-bottom: 1rem;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    .counterfactual-box {
        background: #0F172A88;
        border-left: 3px solid #6366F1;
        padding: 0.6rem 0.8rem;
        border-radius: 4px;
        font-size: 0.9rem;
        margin-top: 0.5rem;
    }
    .metric-card {
        background: #0F172A;
        border: 1px solid #334155;
        border-radius: 8px;
        padding: 1rem;
        text-align: center;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

CATEGORY_CLASSES = {
    "R:SPELL": ("badge-spell", "#A78BFA"),
    "R:VERB:SVA": ("badge-sva", "#F87171"),
    "R:VERB:TENSE": ("badge-tense", "#FB923C"),
    "R:NOUN:NUM": ("badge-noun", "#60A5FA"),
    "R:PREP": ("badge-prep", "#34D399"),
    "M:DET": ("badge-det", "#FBBF24"),
    "R:WO": ("badge-wo", "#818CF8"),
    "R:OTHER": ("badge-other", "#94A3B8"),
}


@st.cache_resource
def get_syntax_and_style():
    """Singleton cached syntax and style modules."""
    syntax_engine = SyntaxEngine()
    critic = SymbolicCritic(syntax_engine)
    linguistic_engine = UniversalLinguisticEngine()
    style_analyzer = StyleAnalyzer(syntax_engine)
    style_naturalizer = StyleNaturalizer(style_analyzer)
    return syntax_engine, critic, linguistic_engine, style_analyzer, style_naturalizer


syntax_engine, critic, linguistic_engine, style_analyzer, style_naturalizer = get_syntax_and_style()


# --- Sidebar Configuration ---
with st.sidebar:
    st.image("https://img.icons8.com/isometric/100/artificial-intelligence.png", width=64)
    st.markdown("### **Orto Configuration**")

    # Engine & Provider Selector
    model_choices = {
        "Auto Cascade (OpenRouter GPT-4o-mini + Free Fallback)": "openai/gpt-4o-mini",
        "Google Gemini (gemini-2.0-flash)": "google/gemini-2.0-flash-exp:free",
        "OpenAI (gpt-4o-mini)": "gpt-4o-mini",
        "Nvidia Nemotron Free": "nvidia/nemotron-3.5-lightning:free",
        "Qwen 2.5 72B / 3.8B Free": "qwen/qwen3.8-27b:free",
        "Universal Linguistic Engine (Offline Ultra-Fast)": "offline",
    }
    selected_model_label = st.selectbox(
        "Diagnostic Engine / LLM:",
        list(model_choices.keys()),
        index=0,
        help="Select the active LLM or offline linguistic engine. Automatic cascade fallback is always active to ensure 100% verified responses.",
    )
    selected_model = model_choices[selected_model_label]

    # Optional custom API key
    custom_api_key = st.text_input(
        "API Key (optional override):",
        type="password",
        placeholder="sk-...",
        help="Leave blank to use environment default (.env)",
    )

    enable_critic = st.toggle(
        "Enable Symbolic Critic",
        value=True,
        help="Enforces morphosyntactic invariant assertions (SVA, dependency tree integrity)",
    )
    enable_style = st.toggle(
        "Enable Stylometry Analysis",
        value=True,
        help="Calculates burstiness and detects synthetic AI markers",
    )
    max_refinements = st.slider(
        "Max Refinement Retries",
        min_value=0,
        max_value=3,
        value=1,
        help="Number of reflection turns on critic rejection",
    )

    st.markdown("---")
    st.markdown("### **Preset Test Cases**")
    preset_options = {
        "Custom Input": "",
        "SVA Intervening Preposition": "The box of old vintage vinyl records were dropped by the movers.",
        "Multiple Orthographic Errors": "She will definately recieve the package untill Friday.",
        "Article & Noun Confusable": "A increase in temperature affect on the final chemical reaction.",
        "Mass Noun & Quantifier": "The goverment provides many informations to the public.",
        "Homophone & Agreement": "Their is no doubt that the committee will approve the budget.",
        "Perfect Aspect Participle": "I have went there three times and saw nothing.",
        "Prepositional Collocations": "Despite of the bad weather, she is married with a doctor and arrived to London.",
        "Double Comparatives & Concord": "He is more taller than his brother, and one of my friend are coming today.",
        "Modal Auxiliary Discordance": "He could went yesterday, but he didn't saw anything.",
        "Synthetic / AI Markers": "Moreover, let us delve into the rich tapestry of modern innovations. It is crucial to foster a beacon of collaboration that underscores our vital role.",
    }
    selected_preset = st.selectbox("Load sample sentence:", list(preset_options.keys()))

    st.markdown("---")
    st.markdown("### **ERRANT Taxonomy Legend**")
    for cat, (cls_name, color) in CATEGORY_CLASSES.items():
        st.markdown(
            f"<span class='errant-pill {cls_name}'>{cat}</span>",
            unsafe_allow_html=True,
        )


# Instantiate engine dynamically based on sidebar settings
llm_client = LLMClient(
    api_key=custom_api_key if custom_api_key.strip() else None,
    model=None if selected_model == "offline" else selected_model,
    mock_mode=(selected_model == "offline"),
)
engine = OrtoEngine(
    syntax_engine=syntax_engine,
    llm_client=llm_client,
    critic=critic,
    linguistic_engine=linguistic_engine,
)


# --- Main Dashboard ---
st.markdown("<div class='main-title'>Orto GEC Engine</div>", unsafe_allow_html=True)
st.markdown(
    "<div class='subtitle'>Neurosymbolic Grammatical Error Correction with Universal Dependency Priors, Multi-Provider LLM Fallback &amp; Stylometry</div>",
    unsafe_allow_html=True,
)

# Text Input Area
default_val = (
    preset_options[selected_preset]
    if selected_preset != "Custom Input"
    else "The box of old vintage vinyl records were dropped by the movers."
)
user_input = st.text_area(
    "Enter raw text to diagnose & correct:",
    value=default_val,
    height=110,
    placeholder="Type or paste any English text here...",
)

col_run, col_clear = st.columns([1, 5])
with col_run:
    run_button = st.button("✨ Analyze Text", type="primary", use_container_width=True)

if user_input:
    # Run pipeline with fallback guarantee
    response = engine.analyze(
        user_input,
        enable_critic=enable_critic,
        max_refinements=max_refinements,
    )

    edits = response.edits
    telemetry = response.telemetry

    # Telemetry Bar
    if telemetry:
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Pipeline Latency", f"{telemetry.latency_ms:.1f} ms")
        c2.metric("Detected Edits", f"{len(edits)}")
        c3.metric("Refinement Cycles", f"{telemetry.refinement_cycles}")
        c4.metric("Critic Status", "PASSED" if telemetry.critic_passed else "FLAGGED")

        engine_tier_name = getattr(telemetry, "engine_tier", "LLM / Verified Fallback")
        st.markdown(
            f"<div class='tier-badge'>⚡ Active Diagnostic Tier: <strong>{html.escape(engine_tier_name)}</strong></div>",
            unsafe_allow_html=True,
        )

    st.markdown("---")

    # Main Tabs: Grammar Diagnostics vs Stylometry
    tab_grammar, tab_style = st.tabs(["🔍 **Grammar & Diagnostics**", "📊 **Stylometry & Rhythm**"])

    with tab_grammar:
        st.markdown("### 🔍 **Surgical Diagnostic Spans**")

        if not edits:
            st.success("✅ No grammatical or orthographic errors detected. The text is verified clean!")
        else:
            # Build annotated HTML view
            annotated_html = ""
            last_idx = 0
            sorted_edits = sorted(edits, key=lambda e: e.span.start_char)

            for i, edit in enumerate(sorted_edits):
                start = edit.span.start_char
                end = edit.span.end_char
                cls_name, _ = CATEGORY_CLASSES.get(edit.errant_type, ("badge-other", "#94A3B8"))

                annotated_html += html.escape(user_input[last_idx:start])
                annotated_html += (
                    f"<span class='highlight-span {cls_name}' title='{edit.errant_type}: {edit.explanation}'>"
                    f"{html.escape(edit.span.original_text)} ➔ {html.escape(edit.replacement)}"
                    f"</span>"
                )
                last_idx = end

            annotated_html += html.escape(user_input[last_idx:])

            st.markdown(
                f"""
                <div style="background: #0F172A; border: 1px solid #334155; border-radius: 8px; padding: 1.2rem; font-size: 1.15rem; line-height: 1.8;">
                    {annotated_html}
                </div>
                """,
                unsafe_allow_html=True,
            )

            st.markdown("<br>", unsafe_allow_html=True)

            # Interactive Accept / Reject Panel
            col_cards, col_preview = st.columns([3, 2])

            with col_cards:
                st.markdown("### 📋 **Pedagogical Diagnostic Cards**")
                accepted_indices = set()

                for idx, edit in enumerate(sorted_edits):
                    cls_name, hex_color = CATEGORY_CLASSES.get(edit.errant_type, ("badge-other", "#94A3B8"))

                    with st.container():
                        st.markdown("<div class='card'>", unsafe_allow_html=True)

                        header_col, toggle_col = st.columns([4, 1])
                        with header_col:
                            critic_badge = (
                                "🛡️ <span style='color: #10B981; font-weight:600;'>Critic Verified</span>"
                                if edit.critic_verified
                                else "⚠️ <span style='color: #F59E0B;'>Unchecked</span>"
                            )
                            st.markdown(
                                f"<span class='errant-pill {cls_name}'>{edit.errant_type}</span> "
                                f"<strong>{edit.linguistic_rule}</strong> &nbsp;|&nbsp; {critic_badge}",
                                unsafe_allow_html=True,
                            )
                        with toggle_col:
                            is_accepted = st.checkbox(
                                "Apply",
                                value=True,
                                key=f"edit_toggle_{idx}",
                            )
                            if is_accepted:
                                accepted_indices.add(idx)

                        st.markdown(
                            f"""
                            <div style="margin-top: 0.6rem;">
                                <strong>Edit:</strong> <del style="color: #EF4444;">{html.escape(edit.span.original_text)}</del> ➔ <span style="color: #10B981; font-weight:700;">{html.escape(edit.replacement)}</span>
                                <br>
                                <span style="color: #CBD5E1; font-size: 0.95rem;">{html.escape(edit.explanation)}</span>
                            </div>
                            <div class='counterfactual-box'>
                                <span style="color: #818CF8; font-weight: 600;">💡 Minimal Counterfactual Pair:</span><br>
                                <em>"{html.escape(edit.counterfactual_example)}"</em>
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )
                        st.markdown("</div>", unsafe_allow_html=True)

            with col_preview:
                st.markdown("### ✍️ **Dynamic Corrected Output**")
                dynamically_corrected = ReverseOffsetPatcher.patch(
                    user_input,
                    sorted_edits,
                    accepted_indices=accepted_indices,
                )

                st.text_area(
                    "Final Corrected Text (Updates in real-time as you toggle edits):",
                    value=dynamically_corrected,
                    height=180,
                )

                # Syntactic Graph Priors Inspector Accordion
                with st.expander("🌳 **Universal Dependency & Morphosyntax Graph**", expanded=False):
                    priors = engine.syntax_engine.extract_priors(user_input)
                    st.markdown("**Key Dependency Relations:**")
                    for dep in priors.get("key_dependencies", []):
                        st.code(dep, language="text")

                    st.markdown("**Subject-Verb Agreement Pairs:**")
                    st.json(priors.get("subject_verb_pairs", []))

    with tab_style:
        if enable_style:
            style_res = style_analyzer.analyze(user_input)
            rep = style_res.report

            # Top Stylometric Metrics
            sm1, sm2, sm3, sm4 = st.columns(4)
            sm1.metric("Burstiness Score (B)", f"{rep.burstiness_score:.2f}", help="std_dev / mean. > 0.5 is natural human cadence")
            sm2.metric("Naturalness Grade", rep.naturalness_grade)
            sm3.metric("AI Cliché Markers", f"{rep.cliche_count}")
            sm4.metric("Passive Voice Density", f"{rep.passive_ratio * 100:.1f}%")

            st.markdown(f"**Diagnosis:** {rep.summary}")
            st.markdown("---")

            col_s1, col_s2 = st.columns(2)
            with col_s1:
                st.markdown("### 🏷️ **Detected AI Markers & Clichés**")
                if rep.detected_markers:
                    for m in rep.detected_markers:
                        st.markdown(f"- <span style='color: #EF4444; font-weight:700;'>{m}</span>", unsafe_allow_html=True)
                else:
                    st.success("No synthetic lexical markers detected.")

                st.markdown("### 📏 **Sentence Length Cadence (Tokens)**")
                if rep.sentence_lengths:
                    st.bar_chart(rep.sentence_lengths)

            with col_s2:
                st.markdown("### 🪄 **Cadence Naturalization & Re-Rhythming**")
                naturalized_preview = style_naturalizer.naturalize(user_input)
                st.text_area("De-clichéd Natural Output:", value=naturalized_preview, height=180)
        else:
            st.info("Enable Stylometry Analysis in the sidebar to view rhythm and synthetic marker metrics.")
