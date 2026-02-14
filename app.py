# app.py
import time
import sqlite3
from datetime import datetime, timezone
from typing import Optional, Tuple, List, Dict

import pandas as pd
import altair as alt
import streamlit as st

from src.config import Config
from src.processing.clean import clean_jobs
from src.processing.skill_extract import extract_skills
from src.processing.role_bucket import classify_role
from src.storage.db import init_db, insert_jobs

from src.data_sources.adzuna_client import fetch_jobs as fetch_jobs_adzuna

# Optional secondary source
try:
    from src.data_sources.jsearch_client import fetch_jobs_jsearch
    HAS_JSEARCH = True
except Exception:
    HAS_JSEARCH = False

# Optional AI enrichment (if you created this file)
try:
    from src.processing.ai_enrichment import enrich_skills_with_ai
    HAS_AI = True
except Exception:
    HAS_AI = False


# -----------------------------
# Page + Style
# -----------------------------
st.set_page_config(
    page_title="SkillPulse — Job Market Intelligence",
    page_icon="📊",
    layout="wide",
)

CUSTOM_CSS = """
<style>
  .block-container { padding-top: 1.2rem; padding-bottom: 2rem; }
  h1, h2, h3 { letter-spacing: -0.02em; }
  .sp-card {
    border: 1px solid rgba(49, 51, 63, 0.15);
    border-radius: 16px;
    padding: 14px 16px;
    background: rgba(255, 255, 255, 0.6);
  }
  .sp-muted { color: rgba(49, 51, 63, 0.65); font-size: 0.95rem; }
  .sp-pill {
    display: inline-block;
    padding: 4px 10px;
    border-radius: 999px;
    border: 1px solid rgba(49, 51, 63, 0.15);
    margin-right: 6px;
    margin-bottom: 6px;
    font-size: 0.9rem;
    background: rgba(255, 255, 255, 0.5);
  }
  .sp-hr { border: none; border-top: 1px solid rgba(49, 51, 63, 0.12); margin: 12px 0; }
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


# -----------------------------
# DB helpers (lightweight, in-app)
# -----------------------------
def _conn() -> sqlite3.Connection:
    return sqlite3.connect(Config.DB_PATH, check_same_thread=False)

def ensure_metrics_table() -> None:
    con = _conn()
    con.execute("""
        CREATE TABLE IF NOT EXISTS runs (
            run_id TEXT PRIMARY KEY,
            run_ts TEXT,
            source TEXT,
            keyword TEXT,
            location TEXT,
            jobs_fetched INTEGER,
            unique_companies INTEGER,
            remote_share REAL
        );
    """)
    con.execute("""
        CREATE TABLE IF NOT EXISTS skills_daily (
            date TEXT,
            skill TEXT,
            count INTEGER,
            PRIMARY KEY(date, skill)
        );
    """)
    con.close()

def upsert_skill_counts(date_str: str, skill_counts: pd.DataFrame) -> None:
    # skill_counts columns: skill, count
    con = _conn()
    for _, r in skill_counts.iterrows():
        con.execute(
            "INSERT OR REPLACE INTO skills_daily(date, skill, count) VALUES (?, ?, ?)",
            (date_str, str(r["skill"]), int(r["count"])),
        )
    con.commit()
    con.close()

def write_run_metrics(run_id: str, run_ts: str, source: str, keyword: str, location: str,
                      jobs_fetched: int, unique_companies: int, remote_share: float) -> None:
    con = _conn()
    con.execute(
        """INSERT OR REPLACE INTO runs
           (run_id, run_ts, source, keyword, location, jobs_fetched, unique_companies, remote_share)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
        (run_id, run_ts, source, keyword, location, jobs_fetched, unique_companies, remote_share),
    )
    con.commit()
    con.close()

def load_runs(days: int = 14) -> pd.DataFrame:
    con = _conn()
    df = pd.read_sql_query(
        """
        SELECT run_ts, source, keyword, location, jobs_fetched, unique_companies, remote_share
        FROM runs
        ORDER BY run_ts DESC
        LIMIT ?
        """,
        con,
        params=(days * 6,),  # rough: up to ~6 refreshes/day
    )
    con.close()
    if df.empty:
        return df
    df["run_ts"] = pd.to_datetime(df["run_ts"], errors="coerce")
    return df

def load_skill_history(skill: str, days: int = 14) -> pd.DataFrame:
    con = _conn()
    df = pd.read_sql_query(
        """
        SELECT date, count
        FROM skills_daily
        WHERE skill = ?
        ORDER BY date DESC
        LIMIT ?
        """,
        con,
        params=(skill, days),
    )
    con.close()
    if df.empty:
        return df
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    return df.sort_values("date")

def get_yesterday_counts(date_str: str) -> pd.DataFrame:
    con = _conn()
    df = pd.read_sql_query(
        """
        SELECT skill, count
        FROM skills_daily
        WHERE date = date(?, '-1 day')
        """,
        con,
        params=(date_str,),
    )
    con.close()
    return df


# -----------------------------
# Analytics helpers
# -----------------------------
def estimate_remote_flag(row: pd.Series) -> bool:
    loc = (row.get("location") or "").lower()
    title = (row.get("title") or "").lower()
    desc = (row.get("description") or "").lower()
    remote_tokens = ["remote", "work from home", "wfh", "distributed"]
    return any(t in loc for t in remote_tokens) or any(t in title for t in remote_tokens) or any(t in desc for t in remote_tokens)

def skill_counts_from_df(df: pd.DataFrame) -> pd.DataFrame:
    # df["skills"] is list
    s = df["skills"].explode()
    counts = s.value_counts().reset_index()
    counts.columns = ["skill", "count"]
    return counts

def top_skill_pairs(df: pd.DataFrame, top_n_skills: int = 20, top_pairs: int = 15) -> pd.DataFrame:
    # For each job, create pairs among its skills; aggregate counts.
    from itertools import combinations
    counts = {}
    # restrict to top skills to keep it fast + readable
    top_sk = set(skill_counts_from_df(df).head(top_n_skills)["skill"].tolist())
    for skills in df["skills"].tolist():
        skills = [s for s in (skills or []) if s in top_sk]
        skills = sorted(set(skills))
        for a, b in combinations(skills, 2):
            key = (a, b)
            counts[key] = counts.get(key, 0) + 1
    out = pd.DataFrame(
        [{"skill_a": k[0], "skill_b": k[1], "co_occurrences": v} for k, v in counts.items()]
    )
    if out.empty:
        return out
    return out.sort_values("co_occurrences", ascending=False).head(top_pairs)

def chart_bar(df: pd.DataFrame, x: str, y: str, title: str) -> alt.Chart:
    return (
        alt.Chart(df)
        .mark_bar()
        .encode(
            x=alt.X(f"{x}:N", sort="-y", title=None),
            y=alt.Y(f"{y}:Q", title=None),
            tooltip=[x, y],
        )
        .properties(title=title, height=300)
    )

def chart_line(df: pd.DataFrame, x: str, y: str, title: str) -> alt.Chart:
    return (
        alt.Chart(df)
        .mark_line(point=True)
        .encode(
            x=alt.X(f"{x}:T", title=None),
            y=alt.Y(f"{y}:Q", title=None),
            tooltip=[x, y],
        )
        .properties(title=title, height=280)
    )


# -----------------------------
# Cached fetch (real-time with cost control)
# -----------------------------
@st.cache_data(ttl=1200, show_spinner=False)
def fetch_jobs_cached(source: str, keyword: str, location: str, results: int) -> List[Dict]:
    if source == "Adzuna":
        return fetch_jobs_adzuna(keyword=keyword, location=location, results=results)
    if source == "JSearch":
        if not HAS_JSEARCH:
            raise RuntimeError("JSearch client not available in this repo.")
        return fetch_jobs_jsearch(keyword=keyword, location=location, page=1)
    raise ValueError("Unknown source")


# -----------------------------
# App init
# -----------------------------
init_db()
ensure_metrics_table()

if "df" not in st.session_state:
    st.session_state.df = pd.DataFrame()
if "last_refresh" not in st.session_state:
    st.session_state.last_refresh = None
if "run_id" not in st.session_state:
    st.session_state.run_id = None

st.title("SkillPulse — Real-Time Job Market & Skills Intelligence")
st.markdown(
    "<div class='sp-muted'>Real-time job feeds → structured skill/role signals → interactive business insights. Built for an MBA-grade deployment deliverable.</div>",
    unsafe_allow_html=True,
)
st.markdown("<hr class='sp-hr'/>", unsafe_allow_html=True)


# -----------------------------
# Sidebar controls
# -----------------------------
with st.sidebar:
    st.header("Controls")
    data_source_options = ["Adzuna"] + (["JSearch"] if HAS_JSEARCH else [])
    source = st.selectbox("Real-time data source", data_source_options)

    keyword = st.text_input("Keyword", value="product manager")
    location = st.text_input("Location", value="United States")

    results = st.slider("Max results per refresh", 25, int(getattr(Config, "MAX_RESULTS", 100)), 50, step=25)
    enable_ai = st.toggle(
        "AI enrichment (optional)",
        value=False,
        help="Uses Gemini skill extraction if configured. Falls back to keyword extraction if not.",
    )

    auto_refresh = st.toggle("Auto-refresh", value=False)
    refresh_every = st.slider("Auto-refresh interval (seconds)", 60, 900, 240, step=30, disabled=not auto_refresh)

    st.markdown("<hr class='sp-hr'/>", unsafe_allow_html=True)
    st.caption("Safety & cost controls: caching + caps + no PII storage.")
    st.caption("Deploy tip: set secrets in Streamlit Cloud to protect API keys.")


# -----------------------------
# Auto refresh (simple)
# -----------------------------
if auto_refresh:
    # A simple "soft" auto-refresh loop: rerun after interval
    # Note: Streamlit doesn't have a built-in rerun timer without extras; this pattern is reliable.
    time.sleep(0.01)
    st.session_state["_next_refresh_ts"] = time.time() + refresh_every


# -----------------------------
# Actions row
# -----------------------------
left, right = st.columns([1, 2])
with left:
    refresh_clicked = st.button("Refresh live data", type="primary", use_container_width=True)
with right:
    if st.session_state.last_refresh:
        st.info(f"Last refreshed: {st.session_state.last_refresh} (UTC)", icon="⏱️")
    else:
        st.info("Not refreshed yet — click **Refresh live data**.", icon="⏱️")

# Auto refresh trigger
if auto_refresh and st.session_state.get("_next_refresh_ts") and time.time() >= st.session_state["_next_refresh_ts"]:
    refresh_clicked = True
    st.session_state["_next_refresh_ts"] = time.time() + refresh_every


# -----------------------------
# Refresh pipeline
# -----------------------------
def run_pipeline() -> Tuple[pd.DataFrame, str]:
    with st.spinner("Fetching real-time jobs and building insights…"):
        jobs = fetch_jobs_cached(source, keyword.strip(), location.strip(), results)

        # Store raw jobs to DB for reproducibility (historical layer)
        insert_jobs(jobs)

        # Clean + enrich
        df = clean_jobs(jobs)

        # Core extraction
        df["skills"] = df["description"].apply(lambda x: extract_skills(x or ""))
        df["role"] = df["title"].apply(lambda x: classify_role(x or ""))

        # Remote estimate
        df["is_remote"] = df.apply(estimate_remote_flag, axis=1)

        # Optional AI: augment skills (cheap mode)
        if enable_ai and HAS_AI and getattr(Config, "GEMINI_API_KEY", None):
            # Only enrich a limited subset for cost control; merge with baseline skills.
            # You can raise this cap later.
            cap = min(25, len(df))
            idxs = df.head(cap).index.tolist()
            for i in idxs:
                try:
                    ai_sk = enrich_skills_with_ai(df.at[i, "description"] or "")
                    if ai_sk:
                        merged = sorted(set((df.at[i, "skills"] or []) + ai_sk))
                        df.at[i, "skills"] = merged
                except Exception:
                    # Keep baseline if AI fails
                    pass

        # Snapshot metrics
        utc_now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
        run_id = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S") + f"-{source.lower()}"
        remote_share = float(df["is_remote"].mean()) if len(df) else 0.0

        write_run_metrics(
            run_id=run_id,
            run_ts=utc_now,
            source=source,
            keyword=keyword.strip(),
            location=location.strip(),
            jobs_fetched=int(len(df)),
            unique_companies=int(df["company"].nunique()) if "company" in df else 0,
            remote_share=remote_share,
        )

        # Store daily skill counts (historical augmentation)
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        sc = skill_counts_from_df(df)
        upsert_skill_counts(today, sc)

        return df, utc_now


if refresh_clicked:
    try:
        df, refreshed_at = run_pipeline()
        st.session_state.df = df
        st.session_state.last_refresh = refreshed_at
        st.session_state.run_id = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
        st.success("Updated with live data.", icon="✅")
    except Exception as e:
        st.error(f"Refresh failed: {e}")


df: pd.DataFrame = st.session_state.df


# -----------------------------
# Main content
# -----------------------------
tabs = st.tabs(["Overview", "Skills", "Roles & Locations", "Trends", "Raw Data", "About"])

# ---------- Overview ----------
with tabs[0]:
    if df.empty:
        st.markdown("<div class='sp-card'>Refresh live data to populate the dashboard.</div>", unsafe_allow_html=True)
    else:
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Jobs (this refresh)", f"{len(df):,}")
        c2.metric("Unique companies", f"{df['company'].nunique():,}")
        c3.metric("Remote share (est.)", f"{(df['is_remote'].mean() * 100):.1f}%")
        c4.metric("Role categories", f"{df['role'].nunique():,}")

        st.markdown("<hr class='sp-hr'/>", unsafe_allow_html=True)

        left, right = st.columns([1.2, 1])
        with left:
            role_counts = df["role"].value_counts().reset_index()
            role_counts.columns = ["role", "count"]
            st.altair_chart(chart_bar(role_counts, "role", "count", "Role mix (current refresh)"), use_container_width=True)
        with right:
            top_sk = skill_counts_from_df(df).head(10)
            st.altair_chart(chart_bar(top_sk, "skill", "count", "Top skills (current refresh)"), use_container_width=True)

        st.markdown("<hr class='sp-hr'/>", unsafe_allow_html=True)

        st.subheader("What changed (quick read)")
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        curr = skill_counts_from_df(df)
        prev = get_yesterday_counts(today)

        if prev.empty or curr.empty:
            st.markdown("<div class='sp-card'><div class='sp-muted'>Not enough history yet. Refresh today and again tomorrow to unlock growth insights.</div></div>", unsafe_allow_html=True)
        else:
            merged = curr.merge(prev, on="skill", how="outer", suffixes=("_today", "_yday")).fillna(0)
            merged["delta"] = merged["count_today"] - merged["count_yday"]
            merged["pct_delta"] = merged.apply(
                lambda r: (r["delta"] / r["count_yday"] * 100) if r["count_yday"] > 0 else (100.0 if r["count_today"] > 0 else 0.0),
                axis=1,
            )
            movers_up = merged.sort_values(["delta", "count_today"], ascending=False).head(5)
            movers_dn = merged.sort_values(["delta", "count_today"], ascending=True).head(5)

            a, b = st.columns(2)
            with a:
                st.markdown("<div class='sp-card'><b>Top risers vs yesterday</b><br/>", unsafe_allow_html=True)
                for _, r in movers_up.iterrows():
                    st.markdown(f"<span class='sp-pill'>{r['skill']}  +{int(r['delta'])} ({r['pct_delta']:.0f}%)</span>", unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)
            with b:
                st.markdown("<div class='sp-card'><b>Top decliners vs yesterday</b><br/>", unsafe_allow_html=True)
                for _, r in movers_dn.iterrows():
                    st.markdown(f"<span class='sp-pill'>{r['skill']}  {int(r['delta'])} ({r['pct_delta']:.0f}%)</span>", unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)

# ---------- Skills ----------
with tabs[1]:
    if df.empty:
        st.markdown("<div class='sp-card'>Refresh live data to view skill analytics.</div>", unsafe_allow_html=True)
    else:
        st.subheader("Skill intelligence")
        sc = skill_counts_from_df(df)
        left, right = st.columns([1, 1])
        with left:
            st.altair_chart(chart_bar(sc.head(20), "skill", "count", "Top 20 skills"), use_container_width=True)
        with right:
            pairs = top_skill_pairs(df, top_n_skills=20, top_pairs=15)
            st.markdown("<div class='sp-card'><b>Skill co-occurrence (top pairs)</b><div class='sp-muted'>Which skills frequently appear together in postings.</div></div>", unsafe_allow_html=True)
            if pairs.empty:
                st.info("Not enough multi-skill postings to compute co-occurrence pairs yet.")
            else:
                st.dataframe(pairs, use_container_width=True, hide_index=True)

        st.markdown("<hr class='sp-hr'/>", unsafe_allow_html=True)
        st.subheader("Skill trend (historical)")
        selected_skill = st.selectbox("Select a skill", options=sc["skill"].tolist() if not sc.empty else [])
        if selected_skill:
            hist = load_skill_history(selected_skill, days=14)
            if hist.empty or len(hist) < 2:
                st.info("Trend history will appear after multiple days of refresh runs.")
            else:
                st.altair_chart(chart_line(hist, "date", "count", f"{selected_skill} — 14-day trend"), use_container_width=True)

# ---------- Roles & Locations ----------
with tabs[2]:
    if df.empty:
        st.markdown("<div class='sp-card'>Refresh live data to view role/location analytics.</div>", unsafe_allow_html=True)
    else:
        st.subheader("Roles & geo signals")

        c1, c2 = st.columns(2)
        with c1:
            role_counts = df["role"].value_counts().reset_index()
            role_counts.columns = ["role", "count"]
            st.altair_chart(chart_bar(role_counts, "role", "count", "Role distribution"), use_container_width=True)

        with c2:
            # Location ranking (simple, depends on API formatting)
            loc_counts = df["location"].value_counts().reset_index()
            loc_counts.columns = ["location", "count"]
            st.altair_chart(chart_bar(loc_counts.head(15), "location", "count", "Top locations (as provided by source)"), use_container_width=True)

        st.markdown("<hr class='sp-hr'/>", unsafe_allow_html=True)
        st.subheader("Company leaderboard")
        comp_counts = df["company"].value_counts().reset_index()
        comp_counts.columns = ["company", "count"]
        st.dataframe(comp_counts.head(20), use_container_width=True, hide_index=True)

# ---------- Trends ----------
with tabs[3]:
    st.subheader("Run-level analytics (from your historical database)")
    runs = load_runs(days=14)
    if runs.empty:
        st.info("No run history yet. Refresh live data a few times to build trend lines.")
    else:
        # Aggregate by day
        runs["date"] = runs["run_ts"].dt.date
        daily = runs.groupby("date", as_index=False).agg(
            jobs_fetched=("jobs_fetched", "sum"),
            unique_companies=("unique_companies", "max"),
            remote_share=("remote_share", "mean"),
        )
        daily["date"] = pd.to_datetime(daily["date"])

        a, b = st.columns(2)
        with a:
            st.altair_chart(chart_line(daily, "date", "jobs_fetched", "Jobs fetched per day (sum)"), use_container_width=True)
        with b:
            st.altair_chart(chart_line(daily, "date", "remote_share", "Remote share per day (avg)"), use_container_width=True)

        st.markdown("<hr class='sp-hr'/>", unsafe_allow_html=True)
        st.markdown("<div class='sp-card'><b>Operational log</b><div class='sp-muted'>Useful for showing real-time refresh activity and defensible analytics in your write-up.</div></div>", unsafe_allow_html=True)
        st.dataframe(runs.sort_values("run_ts", ascending=False).head(30), use_container_width=True)

# ---------- Raw Data ----------
with tabs[4]:
    if df.empty:
        st.markdown("<div class='sp-card'>Refresh live data to view raw postings.</div>", unsafe_allow_html=True)
    else:
        st.subheader("Raw postings (current refresh)")
        show_cols = [c for c in ["title", "company", "location", "role", "is_remote", "created"] if c in df.columns]
        st.dataframe(df[show_cols], use_container_width=True, hide_index=True)

        with st.expander("Preview job description"):
            idx = st.number_input("Row index", min_value=0, max_value=max(0, len(df) - 1), value=0, step=1)
            st.write(df.iloc[int(idx)].get("description", ""))

# ---------- About ----------
with tabs[5]:
    st.subheader("About this dashboard")
    st.markdown(
        """
<div class='sp-card'>
<b>Purpose</b><br/>
SkillPulse converts real-time job postings into structured labor-market intelligence (skills, role mix, location signals, and trends). It is designed as a deployable, business-relevant analytics product for public access.<br/><br/>
<b>Real-time + historical</b><br/>
The app fetches live postings from a jobs API and stores snapshots in a local SQLite database to support trend analytics over time.<br/><br/>
<b>AI layer (optional)</b><br/>
If configured, the dashboard can enrich a subset of postings with LLM-based skill extraction and normalization (cost-capped + cached).<br/><br/>
<b>Disclaimer</b><br/>
Educational use only. Data may be incomplete/delayed. No professional advice. No intentional storage of personally identifiable information.
</div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("<hr class='sp-hr'/>", unsafe_allow_html=True)
    st.markdown(
        "<div class='sp-muted'>Deployment tip: Add your API keys using Streamlit Cloud → App settings → Secrets. Keep rate limits + caching enabled.</div>",
        unsafe_allow_html=True,
    )
