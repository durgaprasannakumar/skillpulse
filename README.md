SkillPulse : Real-Time Job Market & Skills Intelligence Dashboard

SkillPulse is a publicly deployable, real-time analytics dashboard that converts live job postings into structured labor market intelligence. It integrates external job APIs and company career boards to extract skill demand signals, role trends, geographic hiring patterns, and company-level hiring activity.

The system augments real-time data with a lightweight historical database to enable trend analysis and growth detection over time.

Core Capabilities
1. Real-Time Job Market Feed

Pulls live postings via Adzuna and optional JSearch APIs
Company-specific watchlist with direct ATS integration (Greenhouse, Lever, Ashby)
Auto-refresh support with caching and rate controls

2. Skill Intelligence Engine

Extracts standardized technical skills from job descriptions
Classifies roles (PM, Data Scientist, ML Engineer, etc.)
Computes:
    Top in-demand skills
    Skill co-occurrence patterns
    Day-over-day skill growth
    Remote work share

3. Company Watchlist

Direct integration with ATS providers where available
Fallback to real-time aggregated postings filtered by company
Department and location breakdowns
Interactive filtering

4. Historical Augmentation

SQLite-backed storage layer
Daily skill snapshots
Run-level metrics
Trend visualization over time

5. Optional AI Enrichment

Google Gemini integration for semantic skill extraction
Structured normalization of unstructured job descriptions
Controlled API usage with caching safeguards

Architecture Overview
Real-Time Job APIs (Adzuna / JSearch)
            +
Company ATS Boards (Greenhouse / Lever / Ashby)
                    ↓
        Cleaning & Normalization Layer
                    ↓
        Skill Extraction & Role Classification
                    ↓
        Optional LLM Enrichment (Gemini)
                    ↓
        SQLite Historical Store
                    ↓
        Streamlit Interactive Dashboard

Target Audience

MBA students and career switchers seeking data-driven job market insights
Talent acquisition and workforce planning teams
Product and data professionals tracking emerging skill trends
Analysts studying labor market shifts in AI and tech

Business Value

SkillPulse demonstrates how publicly available labor data can be transformed into actionable business intelligence. Potential monetization pathways include:
    SaaS subscription with advanced analytics
    Skill trend alerts and weekly reports
    Enterprise workforce planning dashboards
    API access for HR analytics teams

Disclaimer

This tool is for educational and informational purposes only. Data may be incomplete, delayed, or subject to API provider limitations. The dashboard does not provide professional, legal, financial, or employment advice. No personal data is intentionally collected or stored.

Deployment

The application is built using:
    Python
    Streamlit
    SQLite
    Adzuna API
    Gemini AI API
    Direct ATS board integrations
Public deployment can be performed via Streamlit Cloud.

Why This Project Matters

SkillPulse is not a static visualization exercise. It is a deployable analytics product that demonstrates:
    Real-time data ingestion
    Data engineering best practices
    AI-powered enrichment
    Business-focused insight generation
    Responsible public deployment
