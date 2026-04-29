# Carton Caps Assistant — Gradio Showcase
#
# Prerequisites:
#   1. API running on http://localhost:8000  (uvicorn main:app --port 8000 --reload)
#   2. pip install -r gradio_app/requirements.txt
#
# Run:
#   python gradio_app/app.py     →  http://localhost:7860

import requests
import gradio as gr

API_BASE = "http://localhost:8000"

# Hardcoded user IDs for showcase
USER_IDS = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10"]

# ── CSS ──────────────────────────────────────────────────────────────────────

CSS = """
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

/* ── Base ── */
.gradio-container {
    background: #ECEEF1 !important;
    font-family: 'Inter', 'Segoe UI', system-ui, sans-serif !important;
    min-height: 100vh;
}

footer { display: none !important; }

/* ── Chat panel card ── */
#chat-col {
    background: #FFFFFF;
    border-radius: 20px;
    border: 1px solid rgba(0,0,0,0.06);
    box-shadow: 0 2px 8px rgba(0,0,0,0.04), 0 16px 48px rgba(0,0,0,0.08);
    padding: 36px !important;
}

/* ── Header ── */
#app-header {
    display: flex;
    align-items: center;
    gap: 16px;
    border-bottom: 1px solid #F1F3F6;
    padding-bottom: 20px;
    margin-bottom: 24px;
}
#app-header-icon {
    width: 40px;
    height: 40px;
    background: #0A2540;
    border-radius: 10px;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
}
#app-header-text h2 {
    font-size: 1.05rem;
    font-weight: 700;
    color: #0A2540;
    letter-spacing: -0.02em;
    margin: 0 0 2px 0;
    line-height: 1.2;
}
#app-header-text p {
    font-size: 0.70rem;
    color: #94A3B8;
    margin: 0;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    font-weight: 500;
}

/* ── Status badge ── */
#status-md p {
    font-size: 0.76rem;
    color: #475569;
    margin: 0 0 16px 0;
    padding: 9px 14px;
    background: #F8FAFC;
    border-radius: 8px;
    border: 1px solid #E8EDF2;
    line-height: 1.5;
    font-weight: 400;
}

/* ── Chatbot ── */
#chatbot {
    border: 1px solid #EDF0F4 !important;
    border-radius: 14px !important;
    background: #FAFBFC !important;
}
/* User bubbles — dark navy with white text */
#chatbot .message.user,
#chatbot [data-testid="user"],
#chatbot .user > .message-bubble-border,
#chatbot .bubble-wrap.user .message {
    background: #0A2540 !important;
    border-radius: 14px 14px 4px 14px !important;
}
#chatbot .message.user *,
#chatbot [data-testid="user"] *,
#chatbot .bubble-wrap.user .message * {
    color: #FFFFFF !important;
}
/* Bot bubbles — light slate with dark text */
#chatbot .message.bot,
#chatbot .message.assistant,
#chatbot [data-testid="bot"],
#chatbot .bubble-wrap.bot .message {
    background: #F1F5F9 !important;
    border-radius: 14px 14px 14px 4px !important;
}
#chatbot .message.bot *,
#chatbot .message.assistant *,
#chatbot [data-testid="bot"] *,
#chatbot .bubble-wrap.bot .message * {
    color: #1E293B !important;
}

/* ── Input ── */
#msg-input textarea {
    border-radius: 10px !important;
    border: 1px solid #E2E8F0 !important;
    background: #FAFBFC !important;
    font-size: 0.88rem !important;
    color: #1E293B !important;
    resize: none !important;
    padding: 12px 14px !important;
    transition: border-color 0.2s, box-shadow 0.2s !important;
}
#msg-input textarea:focus {
    border-color: #0A2540 !important;
    box-shadow: 0 0 0 3px rgba(10, 37, 64, 0.08) !important;
    background: #FFFFFF !important;
}
#msg-input textarea::placeholder {
    color: #B0BAC8 !important;
}

/* ── Buttons ── */
#init-btn, #send-btn {
    background: #0A2540 !important;
    color: #FFFFFF !important;
    border: none !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
    font-size: 0.85rem !important;
    letter-spacing: 0.01em !important;
    transition: background 0.2s, transform 0.1s, box-shadow 0.2s !important;
    box-shadow: 0 1px 3px rgba(10,37,64,0.18) !important;
}
#init-btn:hover, #send-btn:hover {
    background: #0F3460 !important;
    box-shadow: 0 4px 12px rgba(10,37,64,0.22) !important;
    transform: translateY(-1px) !important;
}
#init-btn:active, #send-btn:active {
    transform: translateY(0) !important;
}
#clear-btn {
    background: #FFFFFF !important;
    color: #475569 !important;
    border: 1px solid #DDE3EC !important;
    border-radius: 10px !important;
    font-weight: 500 !important;
    font-size: 0.85rem !important;
    transition: background 0.2s, border-color 0.2s !important;
}
#clear-btn:hover {
    background: #F8FAFC !important;
    border-color: #94A3B8 !important;
}
#close-btn {
    background: transparent !important;
    color: #94A3B8 !important;
    border: 1px solid #E8EDF2 !important;
    border-radius: 8px !important;
    font-size: 0.76rem !important;
    font-weight: 500 !important;
    letter-spacing: 0.02em !important;
    transition: color 0.2s, border-color 0.2s, background 0.2s !important;
}
#close-btn:hover {
    color: #DC2626 !important;
    border-color: #FECACA !important;
    background: #FEF2F2 !important;
}
button:disabled {
    opacity: 0.35 !important;
    cursor: not-allowed !important;
    transform: none !important;
    box-shadow: none !important;
}

/* ── Dropdown ── */
#user-dropdown label {
    font-size: 0.76rem !important;
    font-weight: 600 !important;
    color: #64748B !important;
    letter-spacing: 0.03em !important;
    text-transform: uppercase !important;
}
#user-dropdown select, #user-dropdown input {
    border-radius: 10px !important;
    border: 1px solid #E2E8F0 !important;
    font-size: 0.88rem !important;
}

/* ── RAG eval panel ── */
#rag-col {
    background: #0A2540;
    border-radius: 20px;
    border: none;
    box-shadow: 0 2px 8px rgba(0,0,0,0.10), 0 16px 48px rgba(0,0,0,0.14);
    padding: 28px !important;
    align-self: flex-start;
}
#rag-title {
    font-size: 0.65rem;
    font-weight: 700;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: rgba(255,255,255,0.35);
    margin: 0 0 20px 0;
    padding-bottom: 12px;
    border-bottom: 1px solid rgba(255,255,255,0.08);
}
.rag-metric {
    margin-bottom: 18px;
}
.rag-metric-header {
    display: flex;
    justify-content: space-between;
    align-items: baseline;
    margin-bottom: 6px;
}
.rag-metric-name {
    font-size: 0.76rem;
    font-weight: 600;
    color: rgba(255,255,255,0.80);
    letter-spacing: 0.01em;
}
.rag-metric-score {
    font-size: 0.88rem;
    font-weight: 700;
    color: #FFFFFF;
    font-variant-numeric: tabular-nums;
}
.rag-metric-desc {
    font-size: 0.68rem;
    color: rgba(255,255,255,0.65);
    line-height: 1.5;
    margin: 0;
}
.rag-bar-track {
    height: 3px;
    background: rgba(255,255,255,0.10);
    border-radius: 2px;
    margin-top: 6px;
    overflow: hidden;
}
.rag-bar-fill {
    height: 100%;
    border-radius: 2px;
    background: linear-gradient(90deg, #38BDF8, #FFFFFF);
    transition: width 0.5s cubic-bezier(0.4, 0, 0.2, 1);
}
.rag-empty {
    font-size: 0.74rem;
    color: rgba(255,255,255,0.22);
    text-align: center;
    padding: 40px 0;
    line-height: 1.8;
    letter-spacing: 0.01em;
}
"""

# ── API helpers ───────────────────────────────────────────────────────────────

def _api_start_session(user_id: str) -> dict:
    resp = requests.post(
        f"{API_BASE}/sessions",
        json={"user_id": user_id},
        timeout=10,
    )
    resp.raise_for_status()
    return resp.json()


def _api_send_message(session_id: str, user_id: str, message: str) -> dict:
    resp = requests.post(
        f"{API_BASE}/sessions/{session_id}/turns",
        json={"user_id": user_id, "message": message},
        timeout=None,
    )
    resp.raise_for_status()
    return resp.json()


def _api_close_session(session_id: str, user_id: str) -> None:
    requests.delete(
        f"{API_BASE}/sessions/{session_id}",
        json={"user_id": user_id},
        timeout=10,
    )


# ── Gradio handlers ───────────────────────────────────────────────────────────

_CHAT_ENABLED = dict(interactive=True)
_CHAT_DISABLED = dict(interactive=False)


def initialize_session(user_id, current_session_id, current_user_id):
    """Start (or replace) a session for the selected user."""
    if not user_id:
        return (
            current_session_id, current_user_id,
            "⚠ Please select a User ID.",
            gr.update(), gr.update(), gr.update(), gr.update(), gr.update(),
        )

    # Silently close any in-flight session
    if current_session_id:
        try:
            _api_close_session(current_session_id, current_user_id)
        except Exception:
            pass

    try:
        data = _api_start_session(str(user_id))
        session_id = data["session_id"]
        short = session_id[:8]
        status = f"✓ &nbsp;Session active &nbsp;·&nbsp; User **{user_id}** &nbsp;·&nbsp; `{short}…`"
        return (
            session_id,
            str(user_id),
            status,
            gr.update(value=[]),                           # chatbot — clear history
            gr.update(**_CHAT_ENABLED, value=""),          # msg_input
            gr.update(**_CHAT_ENABLED),                    # send_btn
            gr.update(**_CHAT_ENABLED),                    # clear_btn
            gr.update(**_CHAT_ENABLED),                    # close_btn
        )
    except requests.HTTPError as e:
        try:
            msg = e.response.json().get("message", str(e))
        except Exception:
            msg = str(e)
        return (
            "", str(user_id), f"✗ &nbsp;{msg}",
            gr.update(), gr.update(), gr.update(), gr.update(), gr.update(),
        )
    except requests.RequestException as e:
        return (
            "", str(user_id), f"✗ &nbsp;API unreachable — is the server running?",
            gr.update(), gr.update(), gr.update(), gr.update(), gr.update(),
        )


def _build_rag_html(data: dict) -> str:
    """Render the 4 RAG metrics as a styled HTML block."""
    metrics = [
        (
            "Grounding",
            data.get("groundedness_score", 0.0),
            "How well the response is anchored in retrieved evidence.",
        ),
        (
            "Precision",
            data.get("context_precision_score", 0.0),
            "Fraction of retrieved chunks that are actually relevant.",
        ),
        (
            "Recall",
            data.get("context_recall_score", 0.0),
            "Fraction of relevant information that was retrieved.",
        ),
        (
            "Relevance",
            data.get("relevance_score", 0.0),
            "How directly the response addresses the user's question.",
        ),
    ]
    rows = ""
    for name, score, desc in metrics:
        pct = int(round(score * 100))
        rows += (
            f'<div class="rag-metric">'
            f'  <div class="rag-metric-header">'
            f'    <span class="rag-metric-name">{name}</span>'
            f'    <span class="rag-metric-score">{score:.2f}</span>'
            f'  </div>'
            f'  <div class="rag-bar-track"><div class="rag-bar-fill" style="width:{pct}%"></div></div>'
            f'  <p class="rag-metric-desc">{desc}</p>'
            f'</div>'
        )
    return (
        f'<p id="rag-title">Intelligence Metrics</p>'
        f'{rows}'
    )


_RAG_EMPTY_HTML = (
    '<p id="rag-title">Intelligence Metrics</p>'
    '<div class="rag-empty">Send a message<br>to surface metrics.</div>'
)


def send_message(session_id, user_id, message, history):
    """Send one user message and append the assistant reply."""
    message = (message or "").strip()
    if not session_id or not message:
        return history, gr.update(), gr.update(), gr.update(), gr.update(), gr.update(), gr.update(), gr.update()

    history = list(history or [])
    history.append({"role": "user", "content": message})

    active_session_id = session_id
    new_status = gr.update()
    rag_html = gr.update()

    try:
        data = _api_send_message(active_session_id, user_id, message)
        reply = data["response_text"]
        rag_html = gr.update(value=_build_rag_html(data))
    except requests.HTTPError as e:
        if e.response.status_code in (404, 410):
            # Session expired — silently renew and retry once
            try:
                new_data = _api_start_session(user_id)
                active_session_id = new_data["session_id"]
                short = active_session_id[:8]
                new_status = f"✓ &nbsp;Session renewed &nbsp;·&nbsp; User **{user_id}** &nbsp;·&nbsp; `{short}…`"
                data = _api_send_message(active_session_id, user_id, message)
                reply = data["response_text"]
                rag_html = gr.update(value=_build_rag_html(data))
            except Exception:
                reply = "⚠ API unreachable — is the server running?"
        else:
            try:
                reply = f"⚠ {e.response.json().get('message', str(e))}"
            except Exception:
                reply = f"⚠ Unexpected error ({e.response.status_code})"
    except requests.RequestException:
        reply = "⚠ API unreachable — is the server running?"

    history.append({"role": "assistant", "content": reply})
    return history, gr.update(value=""), active_session_id, new_status, gr.update(), gr.update(), gr.update(), rag_html


def clear_input():
    """Empty the message text box."""
    return gr.update(value="")


def close_session(session_id, user_id):
    """Close the active session and reset the UI."""
    if session_id:
        try:
            _api_close_session(session_id, user_id)
        except Exception:
            pass  # close locally regardless

    return (
        "", "",
        "— &nbsp;No active session",
        gr.update(value=[]),                         # chatbot
        gr.update(**_CHAT_DISABLED, value=""),       # msg_input
        gr.update(**_CHAT_DISABLED),                 # send_btn
        gr.update(**_CHAT_DISABLED),                 # clear_btn
        gr.update(**_CHAT_DISABLED),                 # close_btn
        gr.update(value=_RAG_EMPTY_HTML),            # rag_panel
    )


# ── Layout ────────────────────────────────────────────────────────────────────

with gr.Blocks(css=CSS, title="Carton Caps Assistant", theme=gr.themes.Base(font=gr.themes.GoogleFont("Inter"))) as demo:

    session_id_state = gr.State("")
    user_id_state = gr.State("")

    with gr.Row():
        # ── Left spacer ──────────────────────────────────────────────────────
        with gr.Column(scale=1, min_width=0):
            gr.HTML("")

        # ── Chat panel ───────────────────────────────────────────────────────
        with gr.Column(scale=2, elem_id="chat-col"):

            gr.HTML(
                '<div id="app-header">'
                '<div id="app-header-icon">'
                '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">'
                '<path d="M12 2L2 7L12 12L22 7L12 2Z" stroke="white" stroke-width="1.8" stroke-linejoin="round"/>'
                '<path d="M2 17L12 22L22 17" stroke="white" stroke-width="1.8" stroke-linejoin="round"/>'
                '<path d="M2 12L12 17L22 12" stroke="white" stroke-width="1.8" stroke-linejoin="round"/>'
                '</svg>'
                '</div>'
                '<div id="app-header-text">'
                '<h2>Carton Caps Assistant</h2>'
                '<p>Conversational AI &nbsp;&middot;&nbsp; Executive Preview</p>'
                '</div>'
                '</div>'
            )

            # Session controls
            with gr.Row():
                user_dropdown = gr.Dropdown(
                    choices=USER_IDS,
                    value=USER_IDS[0],
                    label="User ID",
                    elem_id="user-dropdown",
                    scale=2,
                )
                init_btn = gr.Button(
                    "Initialize Session",
                    elem_id="init-btn",
                    variant="primary",
                    scale=1,
                )

            status_md = gr.Markdown("— &nbsp;No active session", elem_id="status-md")

            # Chat window
            chatbot = gr.Chatbot(
                value=[],
                type="messages",
                height=400,
                show_label=False,
                elem_id="chatbot",
                layout="bubble",
            )

            # Message input
            msg_input = gr.Textbox(
                placeholder="Type your message and press Enter or click Send…",
                show_label=False,
                interactive=False,
                lines=1,
                max_lines=4,
                elem_id="msg-input",
            )

            # Action buttons
            with gr.Row():
                send_btn = gr.Button(
                    "Send",
                    elem_id="send-btn",
                    variant="primary",
                    interactive=False,
                    scale=2,
                )
                clear_btn = gr.Button(
                    "Clear",
                    elem_id="clear-btn",
                    interactive=False,
                    scale=1,
                )

            close_btn = gr.Button(
                "Close Session",
                elem_id="close-btn",
                interactive=False,
                size="sm",
            )

        # ── RAG eval panel ───────────────────────────────────────────────────
        with gr.Column(scale=1, elem_id="rag-col", min_width=200):
            rag_panel = gr.HTML(value=_RAG_EMPTY_HTML)

        # ── Right spacer ─────────────────────────────────────────────────────
        with gr.Column(scale=1, min_width=0):
            gr.HTML("")

    # ── Shared output list (session state + all reactive components) ──────────
    _session_outputs = [
        session_id_state,
        user_id_state,
        status_md,
        chatbot,
        msg_input,
        send_btn,
        clear_btn,
        close_btn,
    ]

    # Initialize / replace session
    init_btn.click(
        fn=initialize_session,
        inputs=[user_dropdown, session_id_state, user_id_state],
        outputs=_session_outputs,
    )

    # Send message (button or Enter)
    _send_outputs = [chatbot, msg_input, session_id_state, status_md, send_btn, clear_btn, close_btn, rag_panel]

    send_btn.click(
        fn=send_message,
        inputs=[session_id_state, user_id_state, msg_input, chatbot],
        outputs=_send_outputs,
    )
    msg_input.submit(
        fn=send_message,
        inputs=[session_id_state, user_id_state, msg_input, chatbot],
        outputs=_send_outputs,
    )

    # Clear text box only
    clear_btn.click(fn=clear_input, inputs=[], outputs=[msg_input])

    # Close session
    close_btn.click(
        fn=close_session,
        inputs=[session_id_state, user_id_state],
        outputs=_session_outputs + [rag_panel],
    )


if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=8500)

