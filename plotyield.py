import pandas as pd
import plotly.express as px

def plotyield(df):
    if df.empty:
        return None
    fig = px.line(df, x='Date', y='yield', labels={
                        "yield": "%",
                        "Date": "Data"
                    }, title='Meus investimentos')
    fig.add_hline(y=0, line_width=3, line_dash="dash", line_color="white")
    fig.update_traces(line=dict(color="gold", width=4))
    fig.update_layout({
    'plot_bgcolor': 'rgba(0, 0, 0, 1)',
    'paper_bgcolor': 'rgba(0, 0, 0, 1)',
    }, xaxis=dict(showgrid=False),
                yaxis=dict(showgrid=False))

    fig.update_layout(
        font=dict(
            family="Courier New, monospace",
            size=18,
            color="white"
        )
    )
    return fig

def plotvalues(df):
    if df.empty:
        return None
    fig = px.line(df, x='Date', y=['total_yield', 'total_invest'], color_discrete_sequence=['gold', 'red'], labels={
                        "total_yield": "R$",
                        "Date": "Data"
                    }, title='Meus investimentos')
    fig.add_hline(y=0, line_width=3, line_dash="dash", line_color="white")
    fig.update_traces(line=dict(width=4))
    fig.update_layout({
    'plot_bgcolor': 'rgba(0, 0, 0, 1)',
    'paper_bgcolor': 'rgba(0, 0, 0, 1)',
    }, xaxis=dict(showgrid=False),
                yaxis=dict(showgrid=False))

    fig.update_layout(
        font=dict(
            family="Courier New, monospace",
            size=18,
            color="white"
        )
    )
    return fig

# df_quote = pd.read_csv('./static/files/my_investiments.csv')
# print(df_quote.columns)
# plotyield(df_quote).show()
# plotvalues(df_quote).show()