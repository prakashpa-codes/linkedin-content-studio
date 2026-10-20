
import html
import uuid

import requests
import streamlit as st


st.set_page_config(
    page_title="LinkedIn Content Studio",
    page_icon="✍️",
    layout="centered",
    initial_sidebar_state="expanded",
)

GENERATE_WEBHOOK_URL = (
    "https://n8n-djbq.srv2070404.hstgr.cloud/"
    "webhook/linkedin-content-generate"
)
APPROVAL_WEBHOOK_URL = (
    "https://n8n-djbq.srv2070404.hstgr.cloud/"
    "webhook/linkedin-content-approval"
)

LINKEDIN_CHAR_LIMIT = 3000

SUGGESTIONS = [
    ("How developers can use AI responsibly", "Ethics, review habits, guardrails"),
    ("Lessons from shipping my first GenAI app", "A personal build story"),
    ("Why RAG beats fine-tuning for most teams", "A practical opinion piece"),
    ("5 habits of high-impact engineers", "A punchy listicle"),
]

USER_AVATAR = ":material/person:"
ASSISTANT_AVATAR = ":material/auto_awesome:"


# --------------------------------------------------------------------------
# Styling
# --------------------------------------------------------------------------

st.markdown(
    """
<style>
:root {
    --muted: #6B7280;
    --border: #E5E7EB;
    --surface: #F4F5F7;
    --accent: #0A66C2;
}

/* Chrome */
header[data-testid="stHeader"] { background: transparent; }
[data-testid="stDecoration"] { display: none; }
[data-testid="stMain"]:focus,
[data-testid="stMain"]:focus-visible { outline: none; box-shadow: none; }
.block-container { padding-top: 2.5rem; padding-bottom: 7rem; }

/* Sidebar */
[data-testid="stSidebar"] { border-right: 1px solid var(--border); }
[data-testid="stSidebar"] .block-container,
[data-testid="stSidebarUserContent"] { padding-top: 1.25rem; }
.brand { display: flex; align-items: center; gap: .6rem; margin-bottom: 1rem; }
.brand-logo {
    width: 34px; height: 34px; border-radius: 10px;
    background: linear-gradient(135deg, #0A66C2, #6366F1);
    color: #fff; display: grid; place-items: center;
    font-weight: 700; font-size: 15px; letter-spacing: -.02em;
}
.brand-name { font-weight: 600; font-size: 15px; line-height: 1.1; }
.brand-sub { font-size: 12px; color: var(--muted); }
.side-label {
    font-size: 11px; font-weight: 600; letter-spacing: .06em;
    text-transform: uppercase; color: var(--muted); margin: 1.25rem 0 .4rem;
}
.side-topic { font-size: 14px; font-weight: 500; line-height: 1.4; }
.side-meta { font-size: 12px; color: var(--muted); margin-top: .25rem; }
.side-foot { font-size: 12px; color: var(--muted); line-height: 1.5; }

/* Empty state */
.hero { text-align: center; margin: 14vh 0 2rem; }
.hero h1 {
    font-size: 30px; font-weight: 600; letter-spacing: -.02em;
    margin: 0 0 .4rem; padding: 0;
}
.hero p { color: var(--muted); font-size: 15px; margin: 0; }
.st-key-suggestions button {
    justify-content: flex-start; text-align: left;
    padding: .8rem 1rem; min-height: 4.2rem;
    background: #fff; border: 1px solid var(--border);
    transition: background .15s, border-color .15s;
}
.st-key-suggestions button:hover {
    background: var(--surface); border-color: #D1D5DB; color: inherit;
}
.st-key-suggestions button > div,
.st-key-suggestions button [data-testid="stMarkdownContainer"] {
    width: 100%; justify-content: flex-start; text-align: left;
}
.st-key-suggestions button p {
    font-size: 14px; line-height: 1.35; text-align: left; color: var(--muted);
}
.st-key-suggestions button p strong { color: #111827; font-weight: 600; }

/* Chat */
[data-testid="stChatMessage"] { background: transparent; padding: .5rem 0; }
[data-testid="stChatMessage"]:has(.user-msg) {
    flex-direction: row-reverse;
}
[data-testid="stChatMessage"]:has(.user-msg)
    [data-testid="stChatMessageContent"] {
    background: var(--surface); border-radius: 18px;
    padding: .6rem 1rem; max-width: 80%;
    margin-left: auto !important; margin-right: 0 !important;
    flex-grow: 0;
}
[data-testid="stChatMessage"]:has(.user-msg)
    [data-testid="stChatMessageContent"] p { margin: 0; }
[data-testid="stChatMessage"]:has(.user-msg) [data-testid="stMarkdown"],
[data-testid="stChatMessage"]:has(.user-msg) [data-testid="stMarkdownContainer"] {
    margin-bottom: 0 !important;
}
[data-testid="stChatMessage"]:has(.user-msg) [data-testid^="stChatMessageAvatar"] {
    display: none;
}
.msg-label { font-size: 12px; color: var(--muted); margin-bottom: .15rem; }

/* Post card */
.st-key-post_card {
    border-radius: 16px !important;
    box-shadow: 0 1px 2px rgba(16,24,40,.04), 0 4px 16px rgba(16,24,40,.05);
    padding: 1.1rem 1.2rem .9rem !important;
}
.post-head { display: flex; align-items: center; gap: .65rem; }
.post-avatar {
    width: 38px; height: 38px; border-radius: 50%;
    background: linear-gradient(135deg, #0A66C2, #6366F1);
    color: #fff; display: grid; place-items: center; font-weight: 600;
}
.post-title { font-weight: 600; font-size: 14px; line-height: 1.2; }
.post-sub { font-size: 12px; color: var(--muted); }
.pill {
    display: inline-block; font-size: 11px; font-weight: 600;
    padding: 2px 8px; border-radius: 999px; margin-left: auto;
}
.pill-draft { background: #EEF4FF; color: #1E4FD8; }
.pill-approved { background: #ECFDF3; color: #067647; }
.post-foot { font-size: 12px; color: var(--muted); }
.post-foot .over { color: #B42318; font-weight: 600; }

/* Post body: a code block restyled as text, so it keeps the hover copy icon */
[data-testid="stExpander"] [data-testid="stCode"] pre,
.st-key-post_card [data-testid="stCode"] pre {
    background: transparent !important; padding: .25rem 2rem .25rem 0 !important;
}
[data-testid="stExpander"] [data-testid="stCode"] code,
.st-key-post_card [data-testid="stCode"] code {
    font-family: "Inter", sans-serif !important; font-size: 15px !important;
    line-height: 1.6 !important; color: #111827 !important;
    white-space: pre-wrap !important; word-break: break-word;
}

/* Approved banner */
.approved {
    display: flex; gap: .6rem; align-items: center;
    background: #ECFDF3; border: 1px solid #ABEFC6; color: #067647;
    border-radius: 12px; padding: .7rem 1rem; font-size: 14px; margin: .75rem 0;
}
</style>
""",
    unsafe_allow_html=True,
)


# --------------------------------------------------------------------------
# State
# --------------------------------------------------------------------------

defaults = {
    "session_id": str(uuid.uuid4()),
    "topic": "",
    "conversation": [],
    "final_post": "",
    "version": 0,
    "post_status": "empty",
    "notice": "",
    "editing": False,
    "edited": False,
    "edit_nonce": 0,
    "pending_prompt": "",
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value


def start_new_topic():
    st.session_state.session_id = str(uuid.uuid4())
    st.session_state.topic = ""
    st.session_state.conversation = []
    st.session_state.final_post = ""
    st.session_state.version = 0
    st.session_state.post_status = "empty"
    st.session_state.editing = False
    st.session_state.edited = False
    st.session_state.notice = "Ready for a new topic."


def call_webhook(url, payload, timeout, service):
    """POST to an n8n webhook. Returns (result, error_message)."""
    try:
        response = requests.post(url, json=payload, timeout=timeout)
        response.raise_for_status()
        return response.json(), None
    except requests.RequestException as exc:
        return None, f"Could not connect to {service}: {exc}"
    except ValueError:
        return None, f"{service[0].upper()}{service[1:]} returned an invalid response."


def discard_and_reset():
    """Discard the current draft in n8n (if any) and start over."""
    if st.session_state.post_status != "draft":
        start_new_topic()
        st.rerun()

    payload = {
        "action": "discard",
        "topic": st.session_state.topic,
        "finalPost": st.session_state.final_post.strip(),
    }
    with st.spinner("Starting a new topic..."):
        result, error = call_webhook(
            APPROVAL_WEBHOOK_URL, payload, 60, "the approval workflow"
        )
    if error:
        st.error(error)
    elif result.get("status") == "discarded":
        start_new_topic()
        st.rerun()
    else:
        st.error(
            result.get("message", "The current draft could not be discarded.")
        )


def user_bubble(text):
    st.markdown(
        '<span class="user-msg"></span>' + html.escape(text),
        unsafe_allow_html=True,
    )


def use_suggestion(topic):
    st.session_state.pending_prompt = topic


def char_count_html(text):
    count = len(text)
    css = "over" if count > LINKEDIN_CHAR_LIMIT else ""
    return (
        f'<span class="{css}">{count:,}</span> / {LINKEDIN_CHAR_LIMIT:,} characters'
    )


# Display operation messages.
if st.session_state.notice:
    st.toast(st.session_state.notice, icon=":material/check_circle:")
    st.session_state.notice = ""


# --------------------------------------------------------------------------
# Sidebar
# --------------------------------------------------------------------------

with st.sidebar:
    st.markdown(
        """
<div class="brand">
  <div class="brand-logo">in</div>
  <div>
    <div class="brand-name">Content Studio</div>
    <div class="brand-sub">LinkedIn post assistant</div>
  </div>
</div>
""",
        unsafe_allow_html=True,
    )

    if st.button(
        "New post",
        icon=":material/edit_square:",
        width="stretch",
        key="sidebar_new",
    ):
        discard_and_reset()

    st.markdown('<div class="side-label">Current session</div>', unsafe_allow_html=True)
    if st.session_state.post_status == "empty":
        st.markdown(
            '<div class="side-meta">No post yet. Pick a topic to get started.</div>',
            unsafe_allow_html=True,
        )
    else:
        status = st.session_state.post_status
        badge = (
            '<span class="pill pill-approved">Approved</span>'
            if status == "approved"
            else f'<span class="pill pill-draft">Draft · v{st.session_state.version + 1}</span>'
        )
        st.markdown(
            f"""
<div class="side-topic">{html.escape(st.session_state.topic)}</div>
<div class="side-meta" style="display:flex;align-items:center;gap:.5rem">
  {len(st.session_state.conversation)} messages {badge}
</div>
""",
            unsafe_allow_html=True,
        )

    st.markdown('<div class="side-label">How it works</div>', unsafe_allow_html=True)
    st.markdown(
        """
<div class="side-foot">
1. Describe a topic<br>
2. Ask for changes or edit directly<br>
3. Approve to save it to Google Docs
</div>
""",
        unsafe_allow_html=True,
    )


# --------------------------------------------------------------------------
# Composer (docked at the bottom of the page)
# --------------------------------------------------------------------------

if st.session_state.post_status == "empty":
    placeholder = "What would you like to write about?"
elif st.session_state.post_status == "draft":
    placeholder = "Ask for changes, e.g. make it shorter and more conversational"
else:
    placeholder = "Post approved. Start a new post from the sidebar."

prompt = st.chat_input(
    placeholder,
    disabled=st.session_state.post_status == "approved"
    or st.session_state.editing,
)

if st.session_state.pending_prompt:
    prompt = st.session_state.pending_prompt
    st.session_state.pending_prompt = ""


# --------------------------------------------------------------------------
# Empty state
# --------------------------------------------------------------------------

if st.session_state.post_status == "empty" and not prompt:
    st.markdown(
        """
<div class="hero">
  <h1>What should we post about today?</h1>
  <p>Give me a topic. I'll draft it, review it, and polish it with you.</p>
</div>
""",
        unsafe_allow_html=True,
    )
    with st.container(key="suggestions"):
        cols = st.columns(2)
        for i, (title, sub) in enumerate(SUGGESTIONS):
            cols[i % 2].button(
                f"**{title}**  \n{sub}",
                key=f"suggestion_{i}",
                width="stretch",
                on_click=use_suggestion,
                args=(title,),
            )


# --------------------------------------------------------------------------
# Conversation
# --------------------------------------------------------------------------

def render_post_card(post, status):
    version = st.session_state.version + 1
    pill = (
        '<span class="pill pill-approved">Approved</span>'
        if status == "approved"
        else f'<span class="pill pill-draft">Draft · v{version}</span>'
    )
    edited = " · edited by you" if st.session_state.edited else ""

    with st.container(border=True, key="post_card"):
        st.markdown(
            f"""
<div class="post-head">
  <div class="post-avatar">in</div>
  <div>
    <div class="post-title">LinkedIn post</div>
    <div class="post-sub">Reviewed by the studio{edited}</div>
  </div>
  {pill}
</div>
""",
            unsafe_allow_html=True,
        )

        if st.session_state.editing:
            editor_key = (
                f"current_editor_{st.session_state.version}"
                f"_{st.session_state.edit_nonce}"
            )
            new_text = st.text_area(
                "Edit post",
                value=post,
                height=320,
                key=editor_key,
                label_visibility="collapsed",
            )
            st.markdown(
                f'<div class="post-foot">{char_count_html(new_text)}</div>',
                unsafe_allow_html=True,
            )
            spacer, cancel_col, save_col = st.columns([3, 1, 1])
            if cancel_col.button("Cancel", width="stretch"):
                st.session_state.editing = False
                st.rerun()
            if save_col.button("Save", type="primary", width="stretch"):
                if not new_text.strip():
                    st.warning("The current post cannot be empty.")
                else:
                    if new_text.strip() != post.strip():
                        st.session_state.final_post = new_text.strip()
                        st.session_state.edited = True
                    st.session_state.editing = False
                    st.session_state.edit_nonce += 1
                    st.rerun()
            return

        st.code(post, language=None, wrap_lines=True)

        foot_col, *action_cols = st.columns(
            [2.2, 1, 1, 1.25] if status == "draft" else [1]
        )
        foot_col.markdown(
            f'<div class="post-foot" style="padding-top:.55rem">'
            f"{char_count_html(post)}</div>",
            unsafe_allow_html=True,
        )

        if status != "draft":
            return

        edit_col, discard_col, approve_col = action_cols
        if edit_col.button("Edit", icon=":material/edit:", width="stretch"):
            st.session_state.editing = True
            st.rerun()
        discard_clicked = discard_col.button(
            "Discard", icon=":material/delete:", width="stretch"
        )
        approve_clicked = approve_col.button(
            "Approve", icon=":material/check:", type="primary", width="stretch"
        )

    if discard_clicked:
        discard_and_reset()

    if approve_clicked:
        approve_post()


def approve_post():
    post = st.session_state.final_post
    if not post.strip():
        st.warning("The post cannot be empty.")
        return

    payload = {
        "action": "approve",
        "topic": st.session_state.topic,
        "finalPost": post.strip(),
    }
    with st.spinner("Saving approved post to Google Docs..."):
        result, error = call_webhook(
            APPROVAL_WEBHOOK_URL, payload, 60, "the approval workflow"
        )
    if error:
        st.error(error)
    elif result.get("status") == "approved":
        st.session_state.final_post = post.strip()
        st.session_state.post_status = "approved"
        st.session_state.conversation.append(
            {
                "role": "You",
                "label": "Approval",
                "content": "Approved the current post.",
            }
        )
        st.session_state.notice = "Post approved and saved to Google Docs."
        st.rerun()
    else:
        st.error(result.get("message", "The post was not confirmed as saved."))


conversation = st.session_state.conversation
last_assistant = max(
    (i for i, m in enumerate(conversation) if m["role"] != "You"),
    default=-1,
)
assistant_count = 0

for i, message in enumerate(conversation):
    if message["role"] == "You":
        with st.chat_message("user", avatar=USER_AVATAR):
            user_bubble(message["content"])
        continue

    assistant_count += 1
    with st.chat_message("assistant", avatar=ASSISTANT_AVATAR):
        if i == last_assistant:
            st.markdown(
                f'<div class="msg-label">{message["label"]}</div>',
                unsafe_allow_html=True,
            )
            render_post_card(
                st.session_state.final_post, st.session_state.post_status
            )
        else:
            with st.expander(
                f"Version {assistant_count} · {message['label']}",
                icon=":material/history:",
            ):
                st.code(message["content"], language=None, wrap_lines=True)

if st.session_state.post_status == "approved":
    st.markdown(
        '<div class="approved">✓&nbsp; This post has been approved and saved '
        "to Google Docs.</div>",
        unsafe_allow_html=True,
    )
    if st.button(
        "Start a new post", icon=":material/add:", type="primary"
    ):
        start_new_topic()
        st.rerun()


# --------------------------------------------------------------------------
# Handle a new message: first message generates, later ones revise
# --------------------------------------------------------------------------

if prompt and prompt.strip():
    prompt = prompt.strip()
    is_revision = st.session_state.post_status == "draft"

    with st.chat_message("user", avatar=USER_AVATAR):
        user_bubble(prompt)

    if is_revision:
        payload = {
            "sessionId": st.session_state.session_id,
            "topic": st.session_state.topic,
            "revisionRequest": prompt,
            "currentDraft": st.session_state.final_post.strip(),
        }
        spinner_text = "Revising and reviewing your post..."
    else:
        payload = {
            "sessionId": st.session_state.session_id,
            "topic": prompt,
        }
        spinner_text = "Generating and reviewing your post..."

    with st.chat_message("assistant", avatar=ASSISTANT_AVATAR):
        with st.spinner(spinner_text, show_time=True):
            result, error = call_webhook(
                GENERATE_WEBHOOK_URL, payload, 180, "n8n"
            )

        if error:
            st.error(error)
        elif result.get("status") == "success" and result.get("finalPost"):
            if is_revision:
                st.session_state.conversation.extend(
                    [
                        {
                            "role": "You",
                            "label": "Revision Request",
                            "content": prompt,
                        },
                        {
                            "role": "assistant",
                            "label": "Revised and Reviewed Post",
                            "content": result["finalPost"],
                        },
                    ]
                )
                st.session_state.version += 1
                st.session_state.notice = (
                    "Revision completed and reviewed successfully."
                )
            else:
                st.session_state.topic = prompt
                st.session_state.conversation = [
                    {"role": "You", "label": "Topic", "content": prompt},
                    {
                        "role": "assistant",
                        "label": "Reviewed Post",
                        "content": result["finalPost"],
                    },
                ]
                st.session_state.version = 0
                st.session_state.post_status = "draft"
                st.session_state.notice = (
                    "Post generated and reviewed successfully."
                )
            st.session_state.final_post = result["finalPost"]
            st.session_state.edited = False
            st.rerun()
        elif is_revision:
            st.error("The workflow did not return a revised post.")
        else:
            st.error("The workflow did not return a valid post.")
