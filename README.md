SkillPulse : Real-Time Job Market & Skills Intelligence Dashboard

SkillPulse is a publicly deployable, real-time analytics dashboard that transforms live job postings into structured labor market intelligence. It converts unstructured job descriptions into standardized skill signals, role classifications, and hiring trend insights using a modular data pipeline and interactive visualization layer.The system integrates real-time API ingestion with a lightweight historical database to enable trend detection over time.

Features
1. Real-Time Job Market Feed
    1. Live job postings via Adzuna Jobs API
    2. Interactive refresh capability
    3.  Optional auto-refresh with caching safeguards
2. Skill Intelligence Engine
    1. Keyword-based technical skill extraction
    2. Role classification (Product Manager, Data Scientist, ML Engineer, etc.)
    3. Remote-work signal detection
    4. Top skill ranking and growth analysis

3. Historical Trend Layer
    1. SQLite-backed historical storage
    2. Daily skill counts
    3. Run-level metrics (jobs fetched, remote share, company counts)
    4. Day-over-day change detection

4. Interactive Dashboard
    1. Multi-tab UI
    2. Skill distribution charts
    3. Role breakdowns
    4. Location insights
    5. Trend visualizations
    6. Raw job exploration

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
1. MBA students and career switchers seeking data-driven job market insights
2. Talent acquisition and workforce planning teams
3. Product and data professionals tracking emerging skill trends
4. Analysts studying labor market shifts in AI and tech

Business Value
SkillPulse demonstrates how publicly available labor data can be transformed into actionable business intelligence. Potential monetization pathways include:
    1. SaaS subscription with advanced analytics
    2. Skill trend alerts and weekly reports
    3. Enterprise workforce planning dashboards
    4. API access for HR analytics teams

Use Cases
SkillPulse is designed for:
    1. MBA students and career switchers
    2. Workforce planning and HR analytics teams
    3. Product and data professionals tracking emerging AI skill demand
    4. Analysts studying hiring trend shifts
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
   1. git clone <repo_url>
   2. cd skillpulse
2. Create virtual environment
   1. python -m venv venv
   2. source venv/bin/activate  # Mac/Linux
   3. venv\Scripts\activate     # Windows
3. Install dependencies
   pip install -r requirements.txt
4. Configure environment variables
   Create a .env file:
       1. ADZUNA_APP_ID=your_adzuna_id
       2. ADZUNA_APP_KEY=your_adzuna_key
       3. RAPIDAPI_KEY=your_rapidapi_key
       4. GEMINI_API_KEY=your_optional_gemini_key
6. Run locally
   streamlit run app.py

Deployment
The dashboard is deployable via:
    Streamlit Cloud
    Render
    Other Python-compatible hosting services
Environment variables must be configured in deployment settings.

Why This Project Matters
SkillPulse is not a static visualization exercise. It is a deployable analytics product that demonstrates:
    1. Real-time data ingestion
    2. Data engineering best practices
    3. AI-powered enrichment
    4. Business-focused insight generation
    5. Responsible public deployment
