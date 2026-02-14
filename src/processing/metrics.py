import pandas as pd

def skill_trends(df):
    all_skills = df["skills"].explode()
    counts = all_skills.value_counts().reset_index()
    counts.columns = ["skill", "count"]
    return counts
