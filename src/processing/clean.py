import pandas as pd

def clean_jobs(jobs):
    df = pd.DataFrame(jobs)
    df.drop_duplicates(subset="id", inplace=True)
    df.fillna("", inplace=True)
    return df
