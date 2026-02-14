def classify_role(title):
    t = title.lower()
    if "product" in t:
        return "Product Manager"
    if "data scientist" in t:
        return "Data Scientist"
    if "machine learning" in t or "ml engineer" in t:
        return "ML Engineer"
    if "data engineer" in t:
        return "Data Engineer"
    return "Other"