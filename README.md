SkillPulse : Real-Time Job Market & Skills Intelligence Dashboard

SkillPulse is a publicly deployable, real-time analytics dashboard that transforms live job postings into structured labor market intelligence. It converts unstructured job descriptions into standardized skill signals, role classifications, and hiring trend insights using a modular data pipeline and interactive visualization layer.The system integrates real-time API ingestion with a lightweight historical database to enable trend detection over time.

Features
1. Real-Time Job Market Feed
    Live job postings via Adzuna Jobs API
    Interactive refresh capability
    Optional auto-refresh with caching safeguards
2. Skill Intelligence Engine
    Keyword-based technical skill extraction
    Role classification (Product Manager, Data Scientist, ML Engineer, etc.)
    Remote-work signal detection
    Top skill ranking and growth analysis

3. Historical Trend Layer
    SQLite-backed historical storage
    Daily skill counts
    Run-level metrics (jobs fetched, remote share, company counts)
    Day-over-day change detection

4. Interactive Dashboard
    Multi-tab UI
    Skill distribution charts
    Role breakdowns
    Location insights
    Trend visualizations
    Raw job exploration

Architecture Overview

Adzuna Jobs API (Real-Time)
            ↓
Data Cleaning & Normalization
            ↓
Skill Extraction & Role Classification
            ↓
SQLite Historical Storage
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

Use Cases
SkillPulse is designed for:
    MBA students and career switchers
    Workforce planning and HR analytics teams
    Product and data professionals tracking emerging AI skill demand
    Analysts studying hiring trend shifts
It enables structured labor market analysis rather than static job browsing.

Disclaimer: This tool is for educational and informational purposes only. Data may be incomplete, delayed, or subject to API provider limitations. The dashboard does not provide professional, legal, financial, or employment advice. No personal data is intentionally collected or stored.

The application is built using:
    Python
    Streamlit
    SQLite
    Adzuna API
    Gemini AI API
    Direct ATS board integrations
Public deployment can be performed via Streamlit Cloud.

Installation
1. Clone repository
   git clone <repo_url>
   cd skillpulse
2. Create virtual environment
   python -m venv venv
   source venv/bin/activate  # Mac/Linux
   venv\Scripts\activate     # Windows
3. Install dependencies
   pip install -r requirements.txt
4. Configure environment variables
   Create a .env file:
       ADZUNA_APP_ID=your_adzuna_id
       ADZUNA_APP_KEY=your_adzuna_key
       GEMINI_API_KEY=your_optional_gemini_key
5. Run locally
   streamlit run app.py

Deployment
The dashboard is deployable via:
    Streamlit Cloud
    Render
    Other Python-compatible hosting services
Environment variables must be configured in deployment settings.

Why This Project Matters
SkillPulse is not a static visualization exercise. It is a deployable analytics product that demonstrates:
    Real-time data ingestion
    Data engineering best practices
    AI-powered enrichment
    Business-focused insight generation
    Responsible public deployment
