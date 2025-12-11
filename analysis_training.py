import pandas as pd
import plotly.express as px

def get_training_metrics(df):
    """
    Returns KPIs for Training execution.
    """
    # Filter for Training related activities
    training_keywords = ['Training', 'Session', 'Class']
    training_df = df[df['Activity Category'].astype(str).apply(lambda x: any(k.lower() in x.lower() for k in training_keywords))].copy()
    
    total_training_mins = training_df.groupby('Employee Name')['Work Time (Mins)'].sum().sort_values(ascending=False)
    
    # Sessions count (rows)
    session_count = training_df.groupby('Employee Name').size().sort_values(ascending=False)
    
    return total_training_mins, session_count, training_df

def plot_training_leaderboard(total_training_mins, colors=None):
    # Convert to Hours
    total_hours = total_training_mins.copy()
    if isinstance(total_hours, pd.Series):
        total_hours = total_hours.reset_index()
        total_hours.columns = ['Employee Name', 'Work Time (Mins)']
        
    total_hours['Hours'] = (total_hours['Work Time (Mins)'] / 60).round(1)
    
    # Lollipop Chart
    fig = px.scatter(total_hours, x='Hours', y='Employee Name',
                     title="Total Training Hours Delivered (Leaderboard)",
                     text='Hours',
                     color='Hours',
                     color_continuous_scale='Blues')
                     
    fig.update_traces(marker_size=12, textposition='middle right')
    
    for i, row in total_hours.iterrows():
        fig.add_shape(
            type='line',
            x0=0, y0=row['Employee Name'],
            x1=row['Hours'], y1=row['Employee Name'],
            line=dict(color='lightgrey', width=1)
        )
        
    fig.update_layout(yaxis_title=None, xaxis_title="Training Hours", showlegend=False, margin=dict(l=20, r=20, t=40, b=20))
    return fig

def plot_online_vs_offline(training_df, colors=None):
    """
    Donut chart of Online vs Offline.
    """
    def categorize_mode(cat):
        cat = str(cat).lower()
        if 'online' in cat:
            return 'Online'
        elif 'offline' in cat or 'onsite' in cat:
            return 'Offline'
        return 'Other'
        
    training_df['Mode'] = training_df['Activity Category'].apply(categorize_mode)
    
    # Filter out 'Other' if needed, or keep to catch edge cases
    grouped = training_df[training_df['Mode'] != 'Other'].groupby(['Employee Name', 'Mode'])['Work Time (Mins)'].sum().reset_index()
    grouped['Hours'] = (grouped['Work Time (Mins)'] / 60).round(1)
    
    fig = px.bar(grouped, x='Employee Name', y='Hours', color='Mode',
                 title="Session Delivery Mode (Online vs Offline)",
                 labels={'Employee Name': 'Trainer', 'Hours': 'Hours'},
                 barmode='group',
                 text_auto='.1f',
                 color_discrete_sequence=colors if colors else ['#B3E5E5', '#D4EBF7'])  # Very Light Teal, Very Light Blue
    return fig

def plot_sessions_heatmap(training_df, colors=None):
    """
    Calendar heatmap for number of sessions per day.
    """
    grouped = training_df.groupby('Date_Obj').size().reset_index(name='Session Count')
    
    fig = px.bar(grouped, x='Date_Obj', y='Session Count',
                 title="Daily Training Sessions Intensity",
                 color_discrete_sequence=colors if colors else px.colors.qualitative.Pastel)
    return fig
