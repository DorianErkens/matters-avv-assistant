import streamlit as st
import anthropic
import json
import os
from dotenv import load_dotenv
from system_prompt import SYSTEM_PROMPT

load_dotenv()

st.set_page_config(
    page_title="Assistant AVV — Matters",
    page_icon="◆",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
/* Base */
[data-testid="stAppViewContainer"] {
    background-color: #F7F7F5;
    color: #111111;
}
[data-testid="stHeader"] { background-color: #F7F7F5; }
[data-testid="stSidebar"] { background-color: #EFEFED; }

/* Typography */
html, body, [class*="css"] {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    color: #111111;
}

/* Header */
.matters-header {
    display: flex;
    align-items: baseline;
    gap: 12px;
    padding: 24px 0 32px 0;
    border-bottom: 1px solid #E0E0DC;
    margin-bottom: 32px;
}
.matters-logo {
    font-size: 22px;
    font-weight: 700;
    letter-spacing: -0.5px;
    color: #111111;
}
.matters-tag {
    font-size: 12px;
    font-weight: 600;
    color: #111111;
    background-color: #C8FF00;
    padding: 2px 8px;
    border-radius: 2px;
    letter-spacing: 0.5px;
    text-transform: uppercase;
}

/* Section titles */
.section-title {
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    color: #888888;
    margin-bottom: 16px;
}

/* Cards */
.card {
    background-color: #FFFFFF;
    border: 1px solid #E0E0DC;
    border-radius: 6px;
    padding: 20px;
    margin-bottom: 16px;
}
.card-label {
    font-size: 10px;
    font-weight: 600;
    letter-spacing: 1px;
    text-transform: uppercase;
    color: #999999;
    margin-bottom: 4px;
}
.card-value {
    font-size: 14px;
    color: #111111;
    font-weight: 500;
}

/* Enjeux tags */
.tag-row { display: flex; flex-wrap: wrap; gap: 6px; margin-top: 8px; }
.tag {
    font-size: 12px;
    background-color: #F0F0EE;
    border: 1px solid #DDDDD8;
    color: #444444;
    padding: 3px 10px;
    border-radius: 3px;
}
.tag-signal {
    font-size: 12px;
    background-color: #F0FFB0;
    border: 1px solid #A8D400;
    color: #3A6000;
    padding: 3px 10px;
    border-radius: 3px;
}

/* Intervention */
.intervention-type {
    font-size: 18px;
    font-weight: 700;
    color: #111111;
    margin-bottom: 6px;
}
.intervention-justification {
    font-size: 13px;
    color: #666666;
    margin-bottom: 16px;
    font-style: italic;
}

/* Questions */
.question-item {
    padding: 12px 0;
    border-bottom: 1px solid #EBEBЕ8;
}
.question-text {
    font-size: 14px;
    color: #111111;
    margin-bottom: 3px;
}
.question-text.done { color: #AAAAAA; text-decoration: line-through; }
.question-objectif {
    font-size: 11px;
    color: #999999;
}

/* Message consultant */
.message-box {
    background-color: #F5FFCC;
    border-left: 3px solid #8AC800;
    padding: 12px 16px;
    border-radius: 0 4px 4px 0;
    margin-bottom: 16px;
    font-size: 13px;
    color: #333333;
}

/* Empty state */
.empty-state {
    display: flex;
    align-items: center;
    justify-content: center;
    height: 300px;
    color: #BBBBBB;
    font-size: 14px;
    border: 1px dashed #DDDDD8;
    border-radius: 6px;
}

/* Buttons */
.stButton > button {
    background-color: #111111 !important;
    color: #FFFFFF !important;
    font-weight: 600 !important;
    border: none !important;
    border-radius: 4px !important;
    font-size: 13px !important;
}
.stButton > button:hover {
    background-color: #333333 !important;
}

/* Text area */
.stTextArea textarea {
    background-color: #FFFFFF !important;
    border: 1px solid #DDDDD8 !important;
    color: #111111 !important;
    border-radius: 4px !important;
    font-size: 13px !important;
}
.stTextArea textarea:focus {
    border-color: #8AC800 !important;
    box-shadow: 0 0 0 1px #8AC800 !important;
}

/* Chat input */
[data-testid="stChatInput"] textarea {
    background-color: #FFFFFF !important;
    border: 1px solid #DDDDD8 !important;
    color: #111111 !important;
}

/* Chat messages */
[data-testid="stChatMessage"] {
    background-color: #FFFFFF !important;
    border: 1px solid #E8E8E4 !important;
    border-radius: 6px !important;
}

/* Dividers */
hr { border-color: #1E1E1E !important; }

/* Scrollbar */
::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-track { background: #0A0A0A; }
::-webkit-scrollbar-thumb { background: #2A2A2A; border-radius: 2px; }

/* Hide Streamlit branding */
#MainMenu { visibility: hidden; }
footer { visibility: hidden; }
</style>
""", unsafe_allow_html=True)


def init_state():
    defaults = {
        "history": [],
        "diagnostic": None,
        "intervention": None,
        "questions": [],
        "analyzed": False,
        "last_message": "",
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val


def call_claude(messages: list) -> str:
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        st.error("ANTHROPIC_API_KEY manquante dans le fichier .env")
        st.stop()

    client = anthropic.Anthropic(api_key=api_key)
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=2048,
        system=SYSTEM_PROMPT,
        messages=messages,
    )
    return response.content[0].text


def parse_response(raw: str) -> dict:
    raw = raw.strip()
    if not raw:
        raise ValueError("Réponse vide de Claude")

    # Strip markdown code fences
    if "```" in raw:
        parts = raw.split("```")
        for part in parts:
            candidate = part.strip()
            if candidate.startswith("json"):
                candidate = candidate[4:].strip()
            if candidate.startswith("{"):
                try:
                    return json.loads(candidate)
                except json.JSONDecodeError:
                    continue

    # Try direct parse
    if raw.startswith("{"):
        return json.loads(raw)

    # Extract first JSON object found anywhere in the response
    start = raw.find("{")
    end = raw.rfind("}") + 1
    if start != -1 and end > start:
        return json.loads(raw[start:end])

    raise ValueError(f"Pas de JSON valide dans la réponse : {raw[:200]}")


def analyze_notes(notes: str):
    messages = [{"role": "user", "content": f"Notes d'entretien :\n\n{notes}"}]
    raw = call_claude(messages)
    data = parse_response(raw)

    st.session_state.history = messages + [{"role": "assistant", "content": raw}]
    st.session_state.diagnostic = data.get("diagnostic", {})
    st.session_state.intervention = data.get("intervention", {})
    st.session_state.last_message = data.get("message_consultant", "")
    st.session_state.questions = [
        {**q, "statut": "a_poser"} for q in data.get("questions", [])
    ]
    st.session_state.analyzed = True


def send_chat(user_message: str):
    # Remind Claude to stay in JSON format when continuing the conversation
    reminder = "\n\n[Rappel : réponds uniquement en JSON valide, même format que précédemment.]"
    new_msg = {"role": "user", "content": user_message + reminder}
    messages = st.session_state.history + [new_msg]
    raw = call_claude(messages)

    try:
        data = parse_response(raw)
    except (ValueError, json.JSONDecodeError):
        # Fallback : keep existing panel, just update the message
        st.session_state.last_message = raw[:300] if raw else "Réponse non structurée reçue."
        st.session_state.history = messages + [{"role": "assistant", "content": raw}]
        return

    st.session_state.history = messages + [{"role": "assistant", "content": raw}]
    st.session_state.diagnostic = data.get("diagnostic", {})
    st.session_state.intervention = data.get("intervention", {})
    st.session_state.last_message = data.get("message_consultant", "")

    old_statuses = {q["id"]: q["statut"] for q in st.session_state.questions}
    st.session_state.questions = [
        {**q, "statut": old_statuses.get(q["id"], "a_poser")}
        for q in data.get("questions", [])
    ]


def toggle_question(idx: int):
    cycle = {"a_poser": "posee", "posee": "repondue", "repondue": "a_poser"}
    q = st.session_state.questions[idx]
    st.session_state.questions[idx]["statut"] = cycle[q["statut"]]


# ── Init ──────────────────────────────────────────────────────────────────────
init_state()

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="matters-header">
    <span class="matters-logo">Matters</span>
    <span class="matters-tag">AVV Assistant</span>
</div>
""", unsafe_allow_html=True)

# ── Layout ────────────────────────────────────────────────────────────────────
col_left, col_right = st.columns([1, 1], gap="large")

# ── Colonne gauche ────────────────────────────────────────────────────────────
with col_left:
    st.markdown('<div class="section-title">Notes d\'entretien</div>', unsafe_allow_html=True)

    notes_input = st.text_area(
        label="notes",
        label_visibility="collapsed",
        placeholder="Colle tes notes brutes ici — type client, contexte, enjeux, ce qu'ils t'ont dit, taille équipe, stade produit, budget signals...",
        height=180,
    )

    if st.button("Analyser →", use_container_width=True):
        if notes_input.strip():
            with st.spinner("Analyse en cours..."):
                analyze_notes(notes_input)
            st.rerun()
        else:
            st.warning("Ajoute des notes avant d'analyser.")

    if st.session_state.analyzed:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<div class="section-title">Affine avec le client</div>', unsafe_allow_html=True)

        # Chat history (skip first notes message)
        for i, msg in enumerate(st.session_state.history):
            if i == 0:
                continue
            if msg["role"] == "user":
                with st.chat_message("user", avatar="🧑"):
                    st.markdown(msg["content"])
            else:
                try:
                    data = json.loads(msg["content"])
                    assistant_msg = data.get("message_consultant", "")
                    if assistant_msg:
                        with st.chat_message("assistant", avatar="◆"):
                            st.markdown(assistant_msg)
                except Exception:
                    pass

        user_input = st.chat_input("Le client vient de dire...")
        if user_input:
            with st.spinner("Mise à jour..."):
                send_chat(user_input)
            st.rerun()

# ── Colonne droite ────────────────────────────────────────────────────────────
with col_right:
    if not st.session_state.analyzed:
        st.markdown("""
        <div class="empty-state">← Analyse les notes pour commencer</div>
        """, unsafe_allow_html=True)
    else:
        # Message consultant
        if st.session_state.last_message:
            st.markdown(
                f'<div class="message-box">{st.session_state.last_message}</div>',
                unsafe_allow_html=True,
            )

        # ── Diagnostic ────────────────────────────────────────────────────────
        st.markdown('<div class="section-title">Diagnostic</div>', unsafe_allow_html=True)
        diag = st.session_state.diagnostic or {}

        st.markdown('<div class="card">', unsafe_allow_html=True)

        meta_cols = st.columns(3)
        fields = [
            ("Client", diag.get("type_client", "—")),
            ("Stade", diag.get("stade_produit", "—")),
            ("Maturité tech", diag.get("maturite_tech", "—")),
        ]
        for col, (label, val) in zip(meta_cols, fields):
            col.markdown(
                f'<div class="card-label">{label}</div><div class="card-value">{val}</div>',
                unsafe_allow_html=True,
            )

        if diag.get("secteur"):
            st.markdown(
                f'<div class="card-label" style="margin-top:14px;">Secteur</div>'
                f'<div class="card-value">{diag["secteur"]}</div>',
                unsafe_allow_html=True,
            )

        if diag.get("enjeux"):
            st.markdown('<div class="card-label" style="margin-top:14px;">Enjeux détectés</div>', unsafe_allow_html=True)
            tags_html = "".join(f'<span class="tag">{e}</span>' for e in diag["enjeux"])
            st.markdown(f'<div class="tag-row">{tags_html}</div>', unsafe_allow_html=True)

        if diag.get("signaux_importants"):
            st.markdown('<div class="card-label" style="margin-top:14px;">Signaux clés</div>', unsafe_allow_html=True)
            tags_html = "".join(f'<span class="tag-signal">{s}</span>' for s in diag["signaux_importants"])
            st.markdown(f'<div class="tag-row">{tags_html}</div>', unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)

        # ── Intervention recommandée ───────────────────────────────────────────
        st.markdown('<div class="section-title">Intervention recommandée</div>', unsafe_allow_html=True)
        interv = st.session_state.intervention or {}

        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown(
            f'<div class="intervention-type">{interv.get("type", "—")}</div>'
            f'<div class="intervention-justification">{interv.get("justification", "")}</div>',
            unsafe_allow_html=True,
        )

        interv_cols = st.columns(2)
        interv_cols[0].markdown(
            f'<div class="card-label">Durée estimée</div>'
            f'<div class="card-value">{interv.get("duree_estimee", "—")}</div>',
            unsafe_allow_html=True,
        )
        profils = interv.get("profils_suggeres", [])
        interv_cols[1].markdown(
            f'<div class="card-label">Équipe</div>'
            f'<div class="card-value">{", ".join(profils) if profils else "—"}</div>',
            unsafe_allow_html=True,
        )

        etapes = interv.get("etapes_cles", [])
        if etapes:
            st.markdown('<div class="card-label" style="margin-top:14px;">Étapes clés</div>', unsafe_allow_html=True)
            for etape in etapes:
                st.markdown(f'<div class="card-value" style="margin: 4px 0; font-size:13px;">→ {etape}</div>', unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)

        # ── Questions à creuser ────────────────────────────────────────────────
        st.markdown('<div class="section-title">Questions à creuser</div>', unsafe_allow_html=True)

        statut_icons = {"a_poser": "○", "posee": "◎", "repondue": "●"}
        statut_labels = {"a_poser": "À poser", "posee": "Posée", "repondue": "Répondue"}

        for i, q in enumerate(st.session_state.questions):
            statut = q.get("statut", "a_poser")
            is_done = statut == "repondue"
            text_class = "question-text done" if is_done else "question-text"

            q_col, btn_col = st.columns([5, 1])
            with q_col:
                st.markdown(
                    f'<div class="question-item">'
                    f'<div class="{text_class}">{statut_icons[statut]} {q["question"]}</div>'
                    f'<div class="question-objectif">{q.get("objectif", "")}</div>'
                    f'</div>',
                    unsafe_allow_html=True,
                )
            with btn_col:
                st.markdown("<div style='padding-top: 14px;'>", unsafe_allow_html=True)
                if st.button(statut_labels[statut], key=f"q_{i}_{q['id']}"):
                    toggle_question(i)
                    st.rerun()
                st.markdown("</div>", unsafe_allow_html=True)
