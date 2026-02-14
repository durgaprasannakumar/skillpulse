import altair as alt

def bar_chart(df, x, y, title):
    return alt.Chart(df).mark_bar().encode(
        x=x,
        y=y
    ).properties(title=title)
