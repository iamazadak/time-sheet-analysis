import pandas as pd
import plotly.express as px

def get_weekly_summary(df, colors=None):
    """
    Weekly Trends for Dashboard.
    """
    df['Week_Num'] = df['Date_Obj'].dt.isocalendar().week
    
    def check_cat(x, key):
        return key.lower() in str(x).lower()
        
    trends = df.groupby('Week_Num').apply(
        lambda x: pd.Series({
            'Training': x[x['Activity Category'].apply(lambda c: check_cat(c, 'Training'))]['Work Time (Mins)'].sum() / 60,
            'Travel': x[x['Activity Category'].apply(lambda c: check_cat(c, 'Travel'))]['Work Time (Mins)'].sum() / 60,
            'Content': x[x['Activity Category'].apply(lambda c: check_cat(c, 'Content'))]['Work Time (Mins)'].sum() / 60,
            'Admin/Other': x[x['Activity Category'].apply(lambda c: check_cat(c, 'Other') or check_cat(c, 'MIS'))]['Work Time (Mins)'].sum() / 60
        }),
        include_groups=False
    ).reset_index()
    
    
    # Reshape data for heatmap (categories as rows, weeks as columns)
    heatmap_data = trends.set_index('Week_Num')[['Training', 'Travel', 'Content', 'Admin/Other']].T
    
    # Create heatmap
    import plotly.graph_objects as go
    
    fig = go.Figure(data=go.Heatmap(
        z=heatmap_data.values,
        x=heatmap_data.columns,
        y=heatmap_data.index,
        colorscale=[
            [0.0, '#FFFFFF'],    # White for 0
            [0.2, '#E0F2F7'],    # Very light blue
            [0.4, '#B3E5E5'],    # Light teal
            [0.6, '#80D4D4'],    # Medium teal
            [0.8, '#4DB8B8'],    # Darker teal
            [1.0, '#2A9D8F']     # Deep teal
        ],
        text=heatmap_data.values.round(1),
        texttemplate='%{text}h',
        textfont={"size": 11},
        colorbar=dict(title="Hours"),
        hovertemplate='<b>%{y}</b><br>Week %{x}<br>%{z:.1f} hours<extra></extra>'
    ))
    
    fig.update_layout(
        title="Weekly Work Distribution Heatmap (Hours by Category)",
        height=400,
        xaxis=dict(title='Week Number', side='bottom'),
        yaxis=dict(title='Activity Category'),
        margin=dict(l=120, r=40, t=60, b=40)
    )
    return fig

def detect_anomalies(df):
    """
    Returns a dataframe of flags.
    1. Days < 180 mins logged (Simulating "Low Productivity").
    2. Zero minute entries with descriptions (Data Quality).
    """
    # 1. Low Productivity Days
    daily_sums = df.groupby(['Employee Name', 'Date', 'Date_Obj'])['Work Time (Mins)'].sum().reset_index()
    low_prod = daily_sums[daily_sums['Work Time (Mins)'] < 180].copy()
    low_prod['Flag'] = 'Low Productivity (< 3 hrs)'
    
    # 2. Zero min entries with Desc
    zero_mins = df[(df['Work Time (Mins)'] == 0) & (df['Description'].str.len() > 5)].copy()
    zero_mins['Flag'] = 'Zero Mins Logged'
    
    # Combine
    anomalies = pd.concat([
        low_prod[['Date', 'Employee Name', 'Work Time (Mins)', 'Flag']],
        zero_mins[['Date', 'Employee Name', 'Work Time (Mins)', 'Flag', 'Description']]
    ], ignore_index=True)
    
    return anomalies
