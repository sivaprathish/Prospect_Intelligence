"""Modern Streamlit dashboard for Prospect Intelligence."""

from __future__ import annotations

import html
import json
from typing import Any
from urllib.parse import urlparse

import streamlit as st
from dotenv import load_dotenv

from agents import OutreachStrategist, ProspectIntelligenceAgent
from services import FirecrawlService, GeminiService, SeltzService
from workflows import ProspectWorkflow


# ------------------------------------------------------------------
# Application configuration
# ------------------------------------------------------------------

load_dotenv()

st.set_page_config(
    page_title="Prospect Intelligence",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ------------------------------------------------------------------
# Custom styling
# ------------------------------------------------------------------

st.markdown(
    """
    <style>
        /* Main application */
        .stApp {
            background: #f7f8fa;
            color: #0b1f33;
        }

        .block-container {
            max-width: 1500px;
            padding-top: 1.5rem;
            padding-bottom: 3rem;
        }

        /* Sidebar */
        [data-testid="stSidebar"] {
            background: #071c31;
            border-right: 1px solid #16324d;
        }

        [data-testid="stSidebar"] * {
            color: #ffffff;
        }

        [data-testid="stSidebar"] .stRadio label {
            padding: 0.55rem 0.7rem;
            border-radius: 9px;
            margin-bottom: 0.2rem;
        }

        [data-testid="stSidebar"] .stRadio label:hover {
            background: #153554;
        }

        /* Typography */
        h1, h2, h3 {
            color: #0b1f33;
            letter-spacing: -0.02em;
        }

        p {
            color: #475569;
        }

        /* Buttons */
        .stButton > button,
        .stFormSubmitButton > button {
            background: #f97316;
            color: #ffffff;
            border: none;
            border-radius: 9px;
            font-weight: 700;
            padding: 0.65rem 1.25rem;
        }

        .stButton > button:hover,
        .stFormSubmitButton > button:hover {
            background: #ea580c;
            color: #ffffff;
            border: none;
        }

        /* Inputs */
        .stTextInput input,
        .stTextArea textarea {
            background: #ffffff;
            border: 1px solid #dbe2ea;
            border-radius: 9px;
        }

        .stTextInput input:focus,
        .stTextArea textarea:focus {
            border-color: #f97316;
            box-shadow: 0 0 0 1px #f97316;
        }

        /* Generic card */
        .dashboard-card {
            background: #ffffff;
            border: 1px solid #e2e8f0;
            border-radius: 14px;
            padding: 1.2rem;
            margin-bottom: 1rem;
            box-shadow: 0 2px 7px rgba(15, 23, 42, 0.04);
        }

        /* Company header */
        .company-header {
            background: #ffffff;
            border: 1px solid #e2e8f0;
            border-radius: 16px;
            padding: 1.35rem 1.5rem;
            margin-bottom: 1.2rem;
            box-shadow: 0 3px 10px rgba(15, 23, 42, 0.05);
        }

        .company-name {
            color: #0b1f33;
            font-size: 1.8rem;
            font-weight: 800;
            margin-bottom: 0.25rem;
        }

        .company-domain {
            color: #2563eb;
            font-size: 0.95rem;
        }

        .active-badge {
            display: inline-block;
            margin-left: 0.7rem;
            padding: 0.25rem 0.65rem;
            border-radius: 999px;
            color: #15803d;
            background: #dcfce7;
            font-size: 0.75rem;
            font-weight: 700;
            vertical-align: middle;
        }

        /* Metrics */
        .metric-card {
            min-height: 132px;
            background: #ffffff;
            border: 1px solid #e2e8f0;
            border-radius: 14px;
            padding: 1.05rem 1.15rem;
            box-shadow: 0 2px 7px rgba(15, 23, 42, 0.04);
        }

        .metric-icon {
            display: inline-flex;
            width: 42px;
            height: 42px;
            align-items: center;
            justify-content: center;
            border-radius: 11px;
            background: #fff1e8;
            font-size: 1.3rem;
            margin-bottom: 0.6rem;
        }

        .metric-label {
            color: #64748b;
            font-size: 0.82rem;
            font-weight: 600;
        }

        .metric-value {
            color: #0b1f33;
            font-size: 1.8rem;
            font-weight: 800;
            line-height: 1.2;
        }

        .metric-caption {
            color: #16a34a;
            font-size: 0.75rem;
            margin-top: 0.25rem;
        }

        /* Section headings */
        .section-title {
            color: #0b1f33;
            font-size: 1.1rem;
            font-weight: 800;
            margin: 1.5rem 0 0.8rem;
        }

        .card-title {
            color: #0b1f33;
            font-size: 1rem;
            font-weight: 750;
            margin-bottom: 0.7rem;
        }

        /* Tags */
        .tag {
            display: inline-block;
            background: #f1f5f9;
            color: #334155;
            border-radius: 7px;
            padding: 0.3rem 0.65rem;
            margin: 0.2rem 0.25rem 0.2rem 0;
            font-size: 0.78rem;
            font-weight: 600;
        }

        .pain-tag {
            display: inline-block;
            background: #fff1e8;
            color: #c2410c;
            border-radius: 8px;
            padding: 0.4rem 0.7rem;
            margin: 0.25rem;
            font-size: 0.78rem;
            font-weight: 600;
        }

        /* Signal cards */
        .signal-card {
            background: #ffffff;
            border: 1px solid #e2e8f0;
            border-left: 4px solid #f97316;
            border-radius: 11px;
            padding: 1rem;
            margin-bottom: 0.65rem;
        }

        .signal-title {
            color: #0b1f33;
            font-size: 0.95rem;
            font-weight: 750;
        }

        .signal-description {
            color: #64748b;
            font-size: 0.84rem;
            margin-top: 0.35rem;
        }

        /* Priority badges */
        .badge-high {
            background: #dcfce7;
            color: #15803d;
        }

        .badge-medium {
            background: #fef3c7;
            color: #b45309;
        }

        .badge-low {
            background: #dbeafe;
            color: #1d4ed8;
        }

        .priority-badge {
            display: inline-block;
            padding: 0.25rem 0.6rem;
            border-radius: 999px;
            font-size: 0.72rem;
            font-weight: 750;
        }

        /* Person card */
        .person-card {
            background: #ffffff;
            border: 1px solid #e2e8f0;
            border-radius: 13px;
            padding: 1rem;
            margin-bottom: 0.75rem;
            box-shadow: 0 2px 6px rgba(15, 23, 42, 0.03);
        }

        .person-avatar {
            display: flex;
            width: 45px;
            height: 45px;
            align-items: center;
            justify-content: center;
            border-radius: 50%;
            color: #ffffff;
            background: #0b1f33;
            font-weight: 800;
            font-size: 0.9rem;
        }

        .person-name {
            color: #0b1f33;
            font-size: 1rem;
            font-weight: 800;
        }

        .person-title {
            color: #64748b;
            font-size: 0.82rem;
        }

        .fit-score {
            display: inline-flex;
            width: 46px;
            height: 46px;
            align-items: center;
            justify-content: center;
            border: 3px solid #22c55e;
            border-radius: 50%;
            color: #15803d;
            font-size: 0.8rem;
            font-weight: 800;
        }

        /* Strategy */
        .strategy-column {
            min-height: 240px;
            background: #ffffff;
            border: 1px solid #e2e8f0;
            border-radius: 12px;
            padding: 1rem;
        }

        .strategy-heading {
            color: #0b1f33;
            font-size: 0.9rem;
            font-weight: 800;
            margin-bottom: 0.7rem;
        }

        .strategy-item {
            color: #475569;
            font-size: 0.82rem;
            padding: 0.35rem 0;
            border-bottom: 1px solid #f1f5f9;
        }

        /* Source links */
        a {
            color: #2563eb;
            text-decoration: none;
        }

        a:hover {
            color: #f97316;
        }

        /* Tabs */
        .stTabs [data-baseweb="tab-list"] {
            gap: 0.4rem;
            background: #ffffff;
            border: 1px solid #e2e8f0;
            border-radius: 11px;
            padding: 0.35rem;
        }

        .stTabs [data-baseweb="tab"] {
            border-radius: 8px;
            padding: 0.6rem 1rem;
        }

        /* Dataframe */
        [data-testid="stDataFrame"] {
            background: #ffffff;
            border: 1px solid #e2e8f0;
            border-radius: 12px;
            padding: 0.4rem;
        }

        hr {
            border-color: #e2e8f0;
        }
    </style>
    """,
    unsafe_allow_html=True,
)


# ------------------------------------------------------------------
# Helper functions
# ------------------------------------------------------------------

def safe_text(value: Any, default: str = "") -> str:
    """Escape dynamic text before rendering it as HTML."""

    if value is None or value == "":
        value = default

    return html.escape(str(value))


def safe_get(data: dict[str, Any], key: str, default: str = "") -> str:
    """Get a dict value, falling back to default for both missing
    keys AND keys explicitly set to None/empty (common with LLM
    extraction output)."""

    return data.get(key) or default


def safe_float(value: Any, default: float = 0.0) -> float:
    """Coerce a value to float, tolerating None/empty/invalid input."""

    if value is None or value == "":
        return default

    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def valid_url(value: Any) -> str | None:
    """Return safe HTTP/HTTPS URL or None."""

    if not isinstance(value, str):
        return None

    value = value.strip()
    parsed = urlparse(value)

    if parsed.scheme not in {"http", "https"}:
        return None

    if not parsed.netloc:
        return None

    return value


def initials(name: str) -> str:
    """Generate initials for the person avatar."""

    parts = [
        part
        for part in name.strip().split()
        if part
    ]

    if not parts:
        return "?"

    return "".join(
        part[0].upper()
        for part in parts[:2]
    )


def metric_card(
    icon: str,
    label: str,
    value: Any,
    caption: str,
) -> None:
    """Render a dashboard metric card."""

    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-icon">{safe_text(icon)}</div>
            <div class="metric-label">{safe_text(label)}</div>
            <div class="metric-value">{safe_text(value)}</div>
            <div class="metric-caption">{safe_text(caption)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def priority_class(score: float) -> tuple[str, str]:
    """Return priority label and CSS class."""

    if score >= 80:
        return "High", "badge-high"

    if score >= 60:
        return "Medium", "badge-medium"

    return "Low", "badge-low"


def render_tags(
    values: list[str],
    css_class: str = "tag",
) -> None:
    """Render a list as visual tags."""

    if not values:
        st.caption("No information available.")
        return

    tags = "".join(
        (
            f'<span class="{css_class}">'
            f"{safe_text(value)}"
            "</span>"
        )
        for value in values
    )

    st.markdown(tags, unsafe_allow_html=True)


def render_company_header(
    profile: dict[str, Any],
) -> None:
    """Render company identity header."""

    company = safe_get(profile, "company_name", "Prospect Company")
    domain = safe_get(profile, "domain", "")
    industry = safe_get(profile, "industry", "Unknown")

    st.markdown(
        f"""
        <div class="company-header">
            <div class="company-name">
                {safe_text(company)}
                <span class="active-badge">Research complete</span>
            </div>
            <div>
                <span class="company-domain">
                    {safe_text(domain)}
                </span>
                &nbsp;&nbsp;•&nbsp;&nbsp;
                <span style="color:#64748b">
                    {safe_text(industry)}
                </span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_signals(
    signals: list[dict[str, Any]],
) -> None:
    """Render recent company signals."""

    if not signals:
        st.info("No strong company signals were identified.")
        return

    for signal in signals:
        strength = safe_float(signal.get("signal_strength"))

        priority, badge_class = priority_class(strength)
        source = valid_url(signal.get("source_url"))

        # NOTE: this HTML must be built flush-left with no blank lines.
        # Streamlit's markdown renderer treats a blank line followed by
        # indented text as an *indented code block*, which silently
        # breaks unsafe_allow_html rendering partway through the card.
        card_html = (
            '<div class="signal-card">'
            '<div style="display:flex; justify-content:space-between; gap:1rem;">'
            f'<div class="signal-title">{safe_text(safe_get(signal, "signal_type", "Signal"))}</div>'
            f'<span class="priority-badge {badge_class}">{priority} · {strength:.0f}</span>'
            "</div>"
            f'<div class="signal-description">{safe_text(signal.get("summary", ""))}</div>'
            '<div style="color:#475569; font-size:0.82rem; margin-top:0.5rem;">'
            f'{safe_text(signal.get("business_impact", ""))}'
            "</div>"
            "</div>"
        )

        st.markdown(card_html, unsafe_allow_html=True)

        if source:
            st.markdown(
                f"[View supporting source]({source})"
            )


def render_people(
    people: list[dict[str, Any]],
) -> None:
    """Render people-to-reach cards."""

    if not people:
        st.info(
            "No current decision-makers could be verified "
            "from the available public evidence."
        )
        return

    for person in people:
        name = safe_get(person, "name", "Unknown")
        title = safe_get(person, "current_title", "Title unavailable")
        company = safe_get(person, "company", "")
        fit_score = safe_float(person.get("contact_fit_score"))
        profile_url = valid_url(
            person.get("profile_url")
        )

        left, middle, right = st.columns(
            [0.7, 5.6, 1.2],
            vertical_alignment="center",
        )

        with left:
            st.markdown(
                f"""
                <div class="person-avatar">
                    {safe_text(initials(name))}
                </div>
                """,
                unsafe_allow_html=True,
            )

        with middle:
            st.markdown(
                f"""
                <div class="person-name">
                    {safe_text(name)}
                </div>
                <div class="person-title">
                    {safe_text(title)}
                    {" · " + safe_text(company) if company else ""}
                </div>
                """,
                unsafe_allow_html=True,
            )

        with right:
            st.markdown(
                f"""
                <div class="fit-score">
                    {fit_score:.0f}
                </div>
                """,
                unsafe_allow_html=True,
            )

        detail_left, detail_right = st.columns(2)

        with detail_left:
            st.markdown("**Matched opportunity**")
            st.write(
                safe_get(person, "matched_opportunity", "Not identified")
            )

            st.markdown("**Department / seniority**")
            st.write(
                f"{safe_get(person, 'department', 'Unknown')} · "
                f"{safe_get(person, 'seniority', 'Unknown')}"
            )

        with detail_right:
            st.markdown("**Recommended conversation topic**")
            st.write(
                safe_get(person, "conversation_topic", "Not available")
            )

            st.markdown("**Employment validation**")
            st.write(
                safe_get(person, "employment_status", "unverified")
                .replace("_", " ")
                .title()
            )

        st.markdown("**Why this person is relevant**")
        st.write(person.get("why_relevant", ""))

        button_col, source_col = st.columns([1, 4])

        with button_col:
            if profile_url:
                st.link_button(
                    "View public profile",
                    profile_url,
                    use_container_width=True,
                )

        with source_col:
            source_urls = [
                url
                for url in (
                    valid_url(value)
                    for value in person.get(
                        "source_urls",
                        [],
                    )
                )
                if url
            ]

            if source_urls:
                with st.expander("Evidence sources"):
                    for url in source_urls:
                        st.markdown(f"- [{url}]({url})")

        st.divider()


def render_strategy_list(
    title: str,
    icon: str,
    values: list[str],
) -> None:
    """Render one strategy column."""

    items = "".join(
        (
            '<div class="strategy-item">'
            f"• {safe_text(value)}"
            "</div>"
        )
        for value in values
    )

    if not items:
        items = (
            '<div class="strategy-item">'
            "No recommendation available."
            "</div>"
        )

    st.markdown(
        f"""
        <div class="strategy-column">
            <div class="strategy-heading">
                {safe_text(icon)} {safe_text(title)}
            </div>
            {items}
        </div>
        """,
        unsafe_allow_html=True,
    )


# ------------------------------------------------------------------
# Session state
# ------------------------------------------------------------------

if "prospect_result" not in st.session_state:
    st.session_state.prospect_result = None


# ------------------------------------------------------------------
# Sidebar
# ------------------------------------------------------------------

with st.sidebar:
    st.markdown(
        """
        <div style="
            font-size:1.25rem;
            font-weight:800;
            margin:0.4rem 0 1.4rem;
        ">
            🎯 Prospect Intelligence
        </div>
        """,
        unsafe_allow_html=True,
    )

    navigation = st.radio(
        "Navigation",
        [
            "Overview",
            "Signals",
            "Opportunities",
            "People to Reach",
            "Outreach Strategy",
            "Sources",
        ],
        label_visibility="collapsed",
    )

    st.divider()

    st.caption(
        "Research stack"
    )

    st.markdown(
        """
        **Firecrawl**  
        Company pages and news

        **Seltz**  
        Market and people research

        **Gemini**  
        Analysis and validation
        """
    )

    st.divider()

    if st.session_state.prospect_result:
        if st.button(
            "Start new research",
            use_container_width=True,
        ):
            st.session_state.prospect_result = None
            st.rerun()


# ------------------------------------------------------------------
# Header
# ------------------------------------------------------------------

title_col, action_col = st.columns(
    [5, 1],
    vertical_alignment="center",
)

with title_col:
    st.title("Prospect Intelligence")
    st.caption(
        "Evidence-backed company research, business "
        "opportunities and decision-maker discovery."
    )

with action_col:
    if st.session_state.prospect_result:
        st.download_button(
            label="Export JSON",
            data=json.dumps(
                st.session_state.prospect_result,
                indent=2,
                default=str,
            ),
            file_name="prospect_intelligence.json",
            mime="application/json",
            use_container_width=True,
        )


# ------------------------------------------------------------------
# Search form
# ------------------------------------------------------------------

if not st.session_state.prospect_result:
    st.markdown(
        '<div class="section-title">Research a company</div>',
        unsafe_allow_html=True,
    )

    with st.container(border=True):
        with st.form("prospect_research_form"):
            first, second = st.columns(2)

            company_name = first.text_input(
                "Company name",
                placeholder="",
            )

            company_domain = second.text_input(
                "Official company domain",
                placeholder="",
                help=(
                    "The official domain helps validate the "
                    "correct company and its current employees."
                ),
            )

            offering = st.text_area(
                "Your offering",
                placeholder=(
                    "Example: We provide enterprise data and "
                    "AI engineering services that improve "
                    "platform reliability, scalability and "
                    "operational efficiency."
                ),
                height=130,
            )

            submitted = st.form_submit_button(
                "Run prospect research",
                type="primary",
                use_container_width=True,
            )

    if submitted:
        if not company_name.strip():
            st.error("Enter the company name.")

        elif not company_domain.strip():
            st.error("Enter the official company domain.")

        elif not offering.strip():
            st.error("Describe your product or service.")

        else:
            try:
                with st.status(
                    "Building prospect intelligence...",
                    expanded=True,
                ) as status:
                    st.write(
                        "🌐 Collecting company evidence "
                        "with Firecrawl..."
                    )

                    st.write(
                        "📊 Researching market context "
                        "with Seltz..."
                    )

                    llm = GeminiService()

                    workflow = ProspectWorkflow(
                        intelligence=ProspectIntelligenceAgent(
                            firecrawl=FirecrawlService(),
                            seltz=SeltzService(),
                            llm=llm,
                        ),
                        outreach=OutreachStrategist(
                            llm=llm,
                        ),
                    )

                    st.write(
                        "👥 Finding and validating current "
                        "decision-makers..."
                    )

                    result = workflow.run(
                        company_name=company_name.strip(),
                        company_domain=company_domain.strip(),
                        offering=offering.strip(),
                    )

                    st.write(
                        "🎯 Ranking business opportunities..."
                    )

                    st.session_state.prospect_result = result

                    status.update(
                        label="Prospect intelligence ready",
                        state="complete",
                        expanded=False,
                    )

                st.rerun()

            except Exception as error:
                st.error(
                    "The research could not be completed."
                )
                st.exception(error)


# ------------------------------------------------------------------
# Dashboard
# ------------------------------------------------------------------

result = st.session_state.prospect_result

if result:
    profile = result.get("profile", {})
    strategy = result.get("strategy") or {}
    opportunities = result.get(
        "ranked_opportunities",
        [],
    )
    signals = profile.get("signals", [])
    people = profile.get("people_to_reach", [])
    summary = profile.get("research_summary", {})

    render_company_header(profile)

    # Dashboard metrics
    metric_columns = st.columns(4)

    with metric_columns[0]:
        metric_card(
            "🗄️",
            "Research Sources",
            summary.get("total_sources", 0),
            "Firecrawl and Seltz",
        )

    with metric_columns[1]:
        strong_signals = sum(
            1
            for signal in signals
            if safe_float(signal.get("signal_strength")) >= 70
        )

        metric_card(
            "📡",
            "Strong Signals",
            strong_signals,
            "High-confidence events",
        )

    with metric_columns[2]:
        metric_card(
            "🎯",
            "Opportunities",
            len(opportunities),
            "Business opportunities",
        )

    with metric_columns[3]:
        high_fit_people = sum(
            1
            for person in people
            if safe_float(person.get("contact_fit_score")) >= 70
        )

        metric_card(
            "👥",
            "People to Reach",
            len(people),
            f"{high_fit_people} high-fit contacts",
        )

    # Navigation sections
    if navigation == "Overview":
        overview_left, overview_right = st.columns(
            [1.1, 1],
        )

        with overview_left:
            st.markdown(
                '<div class="section-title">'
                "Company Profile"
                "</div>",
                unsafe_allow_html=True,
            )

            with st.container(border=True):
                st.write(
                    profile.get(
                        "company_summary",
                        "No company summary available.",
                    )
                )

                st.markdown("**Products and services**")
                render_tags(
                    profile.get(
                        "products_services",
                        [],
                    )
                )

                st.markdown("**Target customers**")
                render_tags(
                    profile.get(
                        "target_customers",
                        [],
                    )
                )

                st.markdown("**Competitors**")
                render_tags(
                    profile.get(
                        "competitors",
                        [],
                    )
                )

        with overview_right:
            st.markdown(
                '<div class="section-title">'
                "Opportunity Score"
                "</div>",
                unsafe_allow_html=True,
            )

            with st.container(border=True):
                if opportunities:
                    top_opportunity = opportunities[0]
                    top_score = safe_float(
                        top_opportunity.get("opportunity_score")
                    )

                    st.markdown(
                        f"### {top_score:.0f}/100"
                    )

                    st.progress(
                        max(
                            0.0,
                            min(top_score / 100, 1.0),
                        )
                    )

                    st.markdown(
                        f"**{safe_text(top_opportunity.get('title', ''))}**"
                    )

                    st.write(
                        top_opportunity.get(
                            "description",
                            "",
                        )
                    )

                    priority = top_opportunity.get(
                        "priority",
                        "Unknown",
                    )

                    st.caption(
                        f"Priority: {priority}"
                    )

                else:
                    st.info(
                        "No opportunities were identified."
                    )

        signal_col, pain_col = st.columns([1.2, 1])

        with signal_col:
            st.markdown(
                '<div class="section-title">'
                "Recent Signals"
                "</div>",
                unsafe_allow_html=True,
            )

            render_signals(signals[:4])

        with pain_col:
            st.markdown(
                '<div class="section-title">'
                "Pain Points & Challenges"
                "</div>",
                unsafe_allow_html=True,
            )

            with st.container(border=True):
                pain_descriptions = [
                    item.get("description", "")
                    for item in profile.get(
                        "pain_points",
                        [],
                    )
                    if item.get("description")
                ]

                challenge_values = profile.get(
                    "challenges",
                    [],
                )

                render_tags(
                    pain_descriptions + challenge_values,
                    css_class="pain-tag",
                )

        st.markdown(
            '<div class="section-title">'
            "Top People to Reach"
            "</div>",
            unsafe_allow_html=True,
        )

        render_people(people[:3])

    elif navigation == "Signals":
        st.markdown(
            '<div class="section-title">'
            "Company Signals"
            "</div>",
            unsafe_allow_html=True,
        )

        render_signals(signals)

        st.markdown(
            '<div class="section-title">'
            "Industry Trends"
            "</div>",
            unsafe_allow_html=True,
        )

        with st.container(border=True):
            render_tags(
                profile.get("industry_trends", [])
            )

    elif navigation == "Opportunities":
        st.markdown(
            '<div class="section-title">'
            "Ranked Business Opportunities"
            "</div>",
            unsafe_allow_html=True,
        )

        if not opportunities:
            st.info(
                "No business opportunities were identified."
            )

        for index, opportunity in enumerate(
            opportunities,
            start=1,
        ):
            score = safe_float(opportunity.get("opportunity_score"))

            priority, badge_class = priority_class(
                score
            )

            with st.container(border=True):
                top, score_col = st.columns(
                    [5, 1],
                    vertical_alignment="center",
                )

                with top:
                    st.markdown(
                        f"### {index}. "
                        f"{safe_text(opportunity.get('title', ''))}"
                    )

                    st.write(
                        opportunity.get(
                            "description",
                            "",
                        )
                    )

                with score_col:
                    st.markdown(
                        f"""
                        <div style="text-align:center">
                            <div class="fit-score">
                                {score:.0f}
                            </div>
                            <br>
                            <span class="
                                priority-badge
                                {badge_class}
                            ">
                                {priority}
                            </span>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

                st.progress(
                    max(
                        0.0,
                        min(score / 100, 1.0),
                    )
                )

                detail1, detail2, detail3 = st.columns(3)

                detail1.metric(
                    "Signal strength",
                    safe_float(opportunity.get("signal_strength")),
                )

                detail2.metric(
                    "Pain-point relevance",
                    safe_float(opportunity.get("pain_point_relevance")),
                )

                detail3.metric(
                    "Business fit",
                    safe_float(opportunity.get("business_fit")),
                )

                st.markdown("**Matched pain point**")
                st.write(
                    opportunity.get(
                        "matched_pain_point",
                        "",
                    )
                )

    elif navigation == "People to Reach":
        st.markdown(
            '<div class="section-title">'
            "Recommended People to Reach"
            "</div>",
            unsafe_allow_html=True,
        )

        st.caption(
            "People are included only when public evidence "
            "supports their current title and employer."
        )

        render_people(people)

    elif navigation == "Outreach Strategy":
        st.markdown(
            '<div class="section-title">'
            "Outreach Strategy"
            "</div>",
            unsafe_allow_html=True,
        )

        if not strategy:
            st.info(
                "No outreach strategy is available."
            )

        else:
            approach_col, value_col = st.columns(2)

            with approach_col:
                with st.container(border=True):
                    st.markdown(
                        "### Recommended Approach"
                    )
                    st.write(
                        strategy.get(
                            "recommended_approach",
                            "",
                        )
                    )

            with value_col:
                with st.container(border=True):
                    st.markdown(
                        "### Value Proposition"
                    )
                    st.write(
                        strategy.get(
                            "value_proposition",
                            "",
                        )
                    )

            strategy_columns = st.columns(4)

            with strategy_columns[0]:
                render_strategy_list(
                    "Engagement Angles",
                    "💡",
                    strategy.get(
                        "engagement_angles",
                        [],
                    ),
                )

            with strategy_columns[1]:
                render_strategy_list(
                    "Talking Points",
                    "🎙️",
                    strategy.get(
                        "talking_points",
                        [],
                    ),
                )

            with strategy_columns[2]:
                render_strategy_list(
                    "Discovery Questions",
                    "💬",
                    strategy.get(
                        "discovery_questions",
                        [],
                    ),
                )

            with strategy_columns[3]:
                render_strategy_list(
                    "Next Actions",
                    "📋",
                    strategy.get(
                        "recommended_next_actions",
                        [],
                    ),
                )

    elif navigation == "Sources":
        st.markdown(
            '<div class="section-title">'
            "Research Sources"
            "</div>",
            unsafe_allow_html=True,
        )

        source1, source2, source3 = st.columns(3)

        source1.metric(
            "Firecrawl",
            summary.get("firecrawl_sources", 0),
        )

        source2.metric(
            "Seltz market",
            summary.get("seltz_sources", 0),
        )

        source3.metric(
            "Seltz people",
            summary.get("people_sources", 0),
        )

        source_urls = [
            url
            for url in (
                valid_url(value)
                for value in profile.get(
                    "source_urls",
                    [],
                )
            )
            if url
        ]

        if not source_urls:
            st.info("No source URLs are available.")

        for index, url in enumerate(
            source_urls,
            start=1,
        ):
            st.markdown(
                f"{index}. [{url}]({url})"
            )

        st.markdown(
            '<div class="section-title">'
            "People Evidence"
            "</div>",
            unsafe_allow_html=True,
        )

        for person in people:
            source_list = [
                url
                for url in (
                    valid_url(value)
                    for value in person.get(
                        "source_urls",
                        [],
                    )
                )
                if url
            ]

            if source_list:
                with st.expander(
                    safe_get(person, "name", "Unknown person")
                ):
                    for url in source_list:
                        st.markdown(f"- [{url}]({url})")