"""
app.py — Streamlit UI for the PE Ops Due Diligence Brief Generator.

Run with:
    streamlit run src/app.py
"""

import asyncio
import sys
import threading
import queue
from datetime import datetime
from io import StringIO
from pathlib import Path

import streamlit as st

# ---------------------------------------------------------------------------
# Path setup — ensure project root is importable
# ---------------------------------------------------------------------------
BASE_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(BASE_DIR))
sys.path.insert(0, str(BASE_DIR / "src"))

# ---------------------------------------------------------------------------
# Page config — must be the first Streamlit call
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="PE Ops Brief Generator",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ---------------------------------------------------------------------------
# Dark theme CSS
# ---------------------------------------------------------------------------
st.markdown("""
<style>
  /* ── Global ── */
  html, body, [data-testid="stApp"] {
    background-color: #0e1117;
    color: #e8e8e8;
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
  }

  /* ── Hide Streamlit chrome ── */
  #MainMenu, footer, header { visibility: hidden; }

  /* ── Page header ── */
  .pe-header {
    border-bottom: 1px solid #2a2d35;
    padding-bottom: 1.2rem;
    margin-bottom: 2rem;
  }
  .pe-header h1 {
    font-size: 1.65rem;
    font-weight: 700;
    color: #f0f0f0;
    letter-spacing: -0.3px;
    margin: 0 0 0.25rem 0;
  }
  .pe-header p {
    color: #8b8fa8;
    font-size: 0.88rem;
    margin: 0;
  }

  /* ── Section labels ── */
  .section-label {
    font-size: 0.7rem;
    font-weight: 600;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: #c9a84c;
    margin-bottom: 0.5rem;
  }

  /* ── Form card ── */
  .form-card {
    background: #161b27;
    border: 1px solid #2a2d35;
    border-radius: 8px;
    padding: 1.5rem 1.75rem;
    margin-bottom: 1.5rem;
  }

  /* ── Input overrides ── */
  [data-testid="stTextInput"] input,
  [data-testid="stTextArea"] textarea,
  [data-testid="stSelectbox"] select,
  div[data-baseweb="select"] {
    background-color: #1c2030 !important;
    border: 1px solid #2f3347 !important;
    border-radius: 5px !important;
    color: #e8e8e8 !important;
  }
  [data-testid="stTextInput"] input:focus,
  [data-testid="stTextArea"] textarea:focus {
    border-color: #c9a84c !important;
    box-shadow: 0 0 0 2px rgba(201,168,76,0.18) !important;
  }
  label, .stTextInput label, .stTextArea label, .stSelectbox label {
    color: #b0b5c9 !important;
    font-size: 0.82rem !important;
    font-weight: 500 !important;
  }

  /* ── Generate button ── */
  [data-testid="stButton"] > button[kind="primary"] {
    background: #c9a84c;
    color: #0e1117;
    border: none;
    border-radius: 5px;
    font-weight: 700;
    font-size: 0.9rem;
    padding: 0.6rem 1.8rem;
    letter-spacing: 0.02em;
    transition: background 0.15s;
  }
  [data-testid="stButton"] > button[kind="primary"]:hover {
    background: #e0be6a;
  }

  /* ── Download button ── */
  [data-testid="stDownloadButton"] > button {
    background: transparent;
    border: 1px solid #c9a84c;
    color: #c9a84c;
    border-radius: 5px;
    font-weight: 600;
    font-size: 0.85rem;
    padding: 0.45rem 1.2rem;
  }
  [data-testid="stDownloadButton"] > button:hover {
    background: rgba(201,168,76,0.1);
  }

  /* ── Status / progress ── */
  [data-testid="stStatus"] {
    background: #161b27 !important;
    border: 1px solid #2a2d35 !important;
    border-radius: 6px !important;
  }

  /* ── Brief output area ── */
  .brief-wrapper {
    background: #161b27;
    border: 1px solid #2a2d35;
    border-radius: 8px;
    padding: 2rem 2.25rem;
  }
  .brief-wrapper h1 { color: #f0f0f0; font-size: 1.4rem; border-bottom: 1px solid #2a2d35; padding-bottom: 0.5rem; }
  .brief-wrapper h2 { color: #c9a84c; font-size: 1.05rem; margin-top: 1.8rem; }
  .brief-wrapper h3 { color: #d4d8ea; font-size: 0.95rem; }
  .brief-wrapper p  { color: #c5c9dc; line-height: 1.7; }
  .brief-wrapper li { color: #c5c9dc; line-height: 1.6; }
  .brief-wrapper table { border-collapse: collapse; width: 100%; }
  .brief-wrapper th { background: #1f2535; color: #c9a84c; padding: 0.5rem 0.75rem; font-size: 0.8rem; text-align: left; }
  .brief-wrapper td { padding: 0.45rem 0.75rem; border-bottom: 1px solid #242836; color: #c5c9dc; font-size: 0.85rem; }
  .brief-wrapper code { background: #1c2030; border-radius: 3px; padding: 0.1em 0.35em; font-size: 0.85em; }
  .brief-wrapper blockquote { border-left: 3px solid #c9a84c; margin: 0.75rem 0; padding-left: 1rem; color: #8b8fa8; }

  /* ── Divider ── */
  hr { border-color: #2a2d35 !important; }

  /* ── Error box ── */
  [data-testid="stAlert"] {
    background: #1e1424 !important;
    border: 1px solid #5c2d3f !important;
    color: #f0a0a8 !important;
    border-radius: 6px !important;
  }
</style>
""", unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------------
st.markdown("""
<div class="pe-header">
  <h1>PE Ops Due Diligence Brief Generator</h1>
  <p>Middle market buyout targets · $50M–$500M EV · Operational intelligence in minutes</p>
</div>
""", unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Layout: form left, output right
# ---------------------------------------------------------------------------
col_form, col_out = st.columns([1, 1.6], gap="large")

with col_form:
    st.markdown('<div class="section-label">Target Details</div>', unsafe_allow_html=True)

    company_name = st.text_input(
        "Company name *",
        placeholder="e.g. Acme Packaging",
        key="company_name",
    )

    description = st.text_area(
        "Company description *",
        placeholder=(
            "2–5 sentences on the business: what they do, who they serve, "
            "revenue model, and any known ownership history."
        ),
        height=130,
        key="description",
    )

    industry = st.text_input(
        "Industry vertical *",
        placeholder="e.g. Industrial Packaging, Healthcare Services, Business Services",
        key="industry",
    )

    ev_range = st.selectbox(
        "EV range *",
        options=["$50–100M", "$100–250M", "$250–500M"],
        index=1,
        key="ev_range",
    )

    context_notes = st.text_area(
        "Context notes (optional)",
        placeholder=(
            "Deal-specific context: ownership history, known ops issues, "
            "thesis hooks, key-man concerns, customer concentration flags…"
        ),
        height=100,
        key="context_notes",
    )

    st.markdown("<br>", unsafe_allow_html=True)

    generate_clicked = st.button(
        "Generate Brief",
        type="primary",
        use_container_width=True,
        disabled=st.session_state.get("generating", False),
    )


# ---------------------------------------------------------------------------
# Generation logic
# ---------------------------------------------------------------------------

def run_async_in_thread(coro, result_queue: queue.Queue):
    """Run an async coroutine in a dedicated event loop on a worker thread."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        result = loop.run_until_complete(coro)
        result_queue.put(("ok", result))
    except Exception as exc:
        result_queue.put(("err", exc))
    finally:
        loop.close()


with col_out:
    # ── Validation & trigger ──────────────────────────────────────────────
    if generate_clicked:
        missing = []
        if not company_name.strip():
            missing.append("Company name")
        if not description.strip():
            missing.append("Company description")
        if not industry.strip():
            missing.append("Industry vertical")

        if missing:
            st.error(f"Please fill in: {', '.join(missing)}")
        else:
            st.session_state["generating"] = True
            st.session_state["brief_result"] = None
            st.session_state["brief_error"] = None
            st.session_state["brief_inputs"] = {
                "company_name": company_name.strip(),
                "description": description.strip(),
                "industry": industry.strip(),
                "ev_range": ev_range,
                "context_notes": context_notes.strip(),
            }
            st.rerun()

    # ── Active generation ─────────────────────────────────────────────────
    if st.session_state.get("generating") and not st.session_state.get("brief_result"):
        inputs = st.session_state["brief_inputs"]

        from generate_brief import generate_brief  # noqa: E402

        steps = [
            "Web research and data pulls (SEC EDGAR, BLS, news)…",
            "Generating executive summary…",
            "Assessing operational risk flags…",
            "Building comps and benchmarks…",
            "Evaluating IT systems maturity…",
            "Mapping value creation levers…",
            "Drafting 100-day plan…",
            "Compiling diligence questions…",
            "Assembling final brief…",
        ]

        with st.status("Generating brief — this takes 1–2 minutes…", expanded=True) as status_box:
            for s in steps:
                status_box.write(f"⏳ {s}")

            result_q: queue.Queue = queue.Queue()
            t = threading.Thread(
                target=run_async_in_thread,
                args=(
                    generate_brief(
                        company_name=inputs["company_name"],
                        description=inputs["description"],
                        industry=inputs["industry"],
                        ev_range=inputs["ev_range"],
                        context_notes=inputs["context_notes"],
                    ),
                    result_q,
                ),
                daemon=True,
            )
            t.start()
            t.join()  # block until complete (Streamlit rerun will pick up state)

            kind, payload = result_q.get_nowait()

            if kind == "ok":
                output_path = payload
                brief_text = Path(output_path).read_text(encoding="utf-8")
                st.session_state["brief_result"] = brief_text
                st.session_state["brief_path"] = output_path
                st.session_state["generating"] = False
                status_box.update(label="Brief ready.", state="complete", expanded=False)
                st.rerun()
            else:
                st.session_state["brief_error"] = str(payload)
                st.session_state["generating"] = False
                status_box.update(label="Generation failed.", state="error", expanded=False)
                st.rerun()

    # ── Error state ───────────────────────────────────────────────────────
    if st.session_state.get("brief_error"):
        st.error(f"**Error:** {st.session_state['brief_error']}")
        if st.button("Try again"):
            st.session_state["brief_error"] = None
            st.rerun()

    # ── Brief display ─────────────────────────────────────────────────────
    if st.session_state.get("brief_result"):
        brief_text = st.session_state["brief_result"]
        inputs = st.session_state.get("brief_inputs", {})
        company = inputs.get("company_name", "Company")
        today = datetime.today().strftime("%Y-%m-%d")
        filename = f"{company.lower().replace(' ', '_')}_ops_brief_{today}.md"

        # Action row: metadata + download
        meta_col, dl_col = st.columns([2, 1])
        with meta_col:
            st.markdown(
                f'<p style="color:#8b8fa8;font-size:0.82rem;margin:0;">'
                f'<strong style="color:#c9a84c;">{company}</strong> · '
                f'{inputs.get("industry","")} · {inputs.get("ev_range","")} · {today}'
                f'</p>',
                unsafe_allow_html=True,
            )
        with dl_col:
            st.download_button(
                label="Download Markdown",
                data=brief_text.encode("utf-8"),
                file_name=filename,
                mime="text/markdown",
                use_container_width=True,
            )

        st.markdown("<br>", unsafe_allow_html=True)

        # Render the brief
        st.markdown('<div class="brief-wrapper">', unsafe_allow_html=True)
        st.markdown(brief_text, unsafe_allow_html=False)
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Generate another brief", use_container_width=False):
            for key in ["brief_result", "brief_error", "brief_path", "brief_inputs", "generating"]:
                st.session_state.pop(key, None)
            st.rerun()

    # ── Empty state ───────────────────────────────────────────────────────
    elif not st.session_state.get("generating") and not st.session_state.get("brief_error"):
        st.markdown("""
<div style="
  height: 420px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: #3d4259;
  border: 1px dashed #2a2d35;
  border-radius: 8px;
  text-align: center;
  padding: 2rem;
">
  <div style="font-size: 2.5rem; margin-bottom: 1rem; opacity: 0.5;">📋</div>
  <div style="font-size: 0.92rem; font-weight: 600; color: #4a5070; margin-bottom: 0.4rem;">
    Brief output will appear here
  </div>
  <div style="font-size: 0.8rem; color: #363b54; max-width: 320px; line-height: 1.6;">
    Fill in the target details on the left and click <strong style="color:#4a5070;">Generate Brief</strong>.
    Generation typically takes 1–2 minutes.
  </div>
</div>
""", unsafe_allow_html=True)
