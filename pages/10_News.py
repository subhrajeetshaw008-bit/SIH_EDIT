import streamlit as st
from html import escape
from urllib.parse import urlparse

from chatbot.web_search import search_web
from utils.auth import render_user_menu

st.set_page_config(
    page_title="Landslide AI News",
    page_icon="📰",
    layout="wide"
)

# =========================
# LOAD CSS
# =========================

with open("assets/styles.css") as css_file:
    st.markdown(f"<style>{css_file.read()}</style>", unsafe_allow_html=True)

# Card styling (each article gets its own box)
st.markdown(
    """
    <style>
    .news-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 14px;
        padding: 18px 22px;
        margin-bottom: 16px;
        box-shadow: 0 2px 8px rgba(15, 23, 42, 0.06);
        transition: box-shadow 0.2s ease, transform 0.2s ease;
    }
    .news-card:hover {
        box-shadow: 0 6px 18px rgba(15, 23, 42, 0.12);
        transform: translateY(-2px);
    }
    .news-source-badge {
        display: inline-block;
        font-size: 0.75rem;
        font-weight: 600;
        padding: 3px 10px;
        border-radius: 999px;
        background: #eef2ff;
        color: #4338ca;
        margin-bottom: 8px;
    }
    .news-card h3 {
        margin: 6px 0 8px 0;
        padding: 0;
        font-size: 1.25rem;
        line-height: 1.3;
        color: #0f172a;
    }
    .news-card p {
        margin: 0 0 12px 0;
        font-size: 0.95rem;
        color: #334155;
    }
    .news-card a {
        font-weight: 600;
        text-decoration: none;
    }
    .news-card a:hover {
        text-decoration: underline;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

render_user_menu()


# =========================
# HELPERS
# =========================

def clean_text(raw, limit=280):
    lines = []
    for line in (raw or "").splitlines():
        line = line.strip()
        # drop scraper junk
        if not line or line.lower().startswith("title:") or line.lower() == "advertisement":
            continue
        lines.append(line)
    text = " ".join(" ".join(lines).split())
    return text[:limit] + "..." if len(text) > limit else text


def render_article(article):
    title = escape(" ".join((article.get("title") or "Untitled").split()))
    url = article.get("url") or ""
    snippet = escape(clean_text(article.get("content")))
    source = escape(urlparse(url).netloc.removeprefix("www.")) if url else "unknown"
    link = (
        f"<a href='{escape(url, quote=True)}' target='_blank' rel='noopener'>Read full article ↗</a>"
        if url else ""
    )

    # single line, no blank lines or indentation, so Markdown can't break the card
    st.markdown(
        f"<div class='news-card'>"
        f"<span class='news-source-badge'>{source}</span>"
        f"<h3>{title}</h3>"
        f"<p>{snippet}</p>"
        f"{link}"
        f"</div>",
        unsafe_allow_html=True,
    )


# =========================
# HEADER
# =========================

st.markdown("<div class='news-shell-anchor'></div>", unsafe_allow_html=True)
st.markdown(
    "<div class='weather-header'>"
    "<div class='main-brand-mark'>▲</div>"
    "<div>"
    "<div class='assistant-kicker'>LANDSLIDE INTELLIGENCE</div>"
    "<h1>News & situation awareness</h1>"
    "<p>Recent landslide and disaster-related news, pulled live.</p>"
    "</div></div>",
    unsafe_allow_html=True,
)

# =========================
# SEARCH
# =========================

st.markdown("<div class='section-kicker'>01 <span>Search Topic</span></div>", unsafe_allow_html=True)

with st.form("news_search"):
    search_column, button_column = st.columns([4, 1])

    with search_column:
        news_query = st.text_input(
            "Search topic",
            value=st.session_state.get("news_query", "landslide Northeast India"),
            label_visibility="collapsed",
            placeholder="e.g. landslide Assam, Manipur flood, NDRF rescue",
        )

    with button_column:
        refresh_clicked = st.form_submit_button("🔍 Search News", use_container_width=True)

if refresh_clicked or "news_results" not in st.session_state:
    st.session_state["news_query"] = news_query
    with st.spinner("Fetching latest news..."):
        st.session_state["news_results"] = search_web(news_query)

results = st.session_state.get("news_results", [])

# =========================
# RESULTS
# =========================

st.markdown("<div class='section-kicker'>02 <span>Latest Articles</span></div>", unsafe_allow_html=True)

if not results:
    st.warning("No news results available right now. Check that TAVILY_API_KEY is valid, then try searching again.")
else:
    for article in results:
        render_article(article)