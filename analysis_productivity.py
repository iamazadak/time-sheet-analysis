import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

def get_productivity_summary(df):
    """
    Calculates total logged minutes and average daily minutes per trainer.
    """
    # Total minutes
    total_mins = df.groupby('Employee Name')['Work Time (Mins)'].sum().sort_values(ascending=False)
    
    # Avg daily minutes
    # Denominator: Unique days worked (where at least one task > 0 mins)
    active_days = df[df['Work Time (Mins)'] > 0].groupby('Employee Name')['Date'].nunique()
    avg_daily_mins = (total_mins / active_days).sort_values(ascending=False)
    
    return total_mins, avg_daily_mins

def plot_total_logged_minutes(total_mins, colors=None):
    # Convert to Hours
    total_hours = total_mins.copy()
    if isinstance(total_hours, pd.Series):
        total_hours = total_hours.reset_index()
        total_hours.columns = ['Employee Name', 'Work Time (Mins)']
        
    total_hours['Hours'] = (total_hours['Work Time (Mins)'] / 60).round(1)
    
    # Lollipop Chart (Dot Plot)
    fig = px.scatter(total_hours, x='Hours', y='Employee Name',
                     title="Total Focus Time per Trainer (Hours)",
                     text='Hours',
                     color='Hours',
                     color_continuous_scale='Blues')
                     
    fig.update_traces(marker_size=12, textposition='middle right')
    
    # Add lines for lollipop effect
    for i, row in total_hours.iterrows():
        fig.add_shape(
            type='line',
            x0=0, y0=row['Employee Name'],
            x1=row['Hours'], y1=row['Employee Name'],
            line=dict(color='lightgrey', width=1)
        )
        
    fig.update_layout(
        yaxis_title=None, 
        xaxis_title="Hours", 
        showlegend=False,
        margin=dict(l=20, r=20, t=40, b=20)
    )
    return fig

def plot_utilization_rate_lollipop(df, capacity_mins=None, colors=None):
    """
    Lollipop version - Real utilization rate (Billable / Capacity).
    """
    if capacity_mins:
        # Utilization based on Capacity
        grouped = df.groupby('Employee Name').apply(
            lambda x: x[x['Is_Billable']]['Work Time (Mins)'].sum() / capacity_mins * 100,
            include_groups=False
        ).sort_values(ascending=False)
        title_text = f"Utilization Scorecard - Lollipop (Target: {capacity_mins/60:.1f} hrs)"
    else:
        # Old Logic
        grouped = df.groupby('Employee Name').apply(
            lambda x: x[x['Is_Billable']]['Work Time (Mins)'].sum() / x['Work Time (Mins)'].sum() * 100 if x['Work Time (Mins)'].sum() > 0 else 0,
            include_groups=False
        ).sort_values(ascending=False)
        title_text = "Utilization Rate - Lollipop (Billable Time %)"
    
    # Prepare DF for Plotly
    plot_df = grouped.reset_index(name='Utilization %')
    
    fig = px.scatter(plot_df, x='Utilization %', y='Employee Name',
                     title=title_text,
                     text=plot_df['Utilization %'].apply(lambda x: f"{x:.1f}%"),
                     color='Utilization %',
                     color_continuous_scale='Teal')
    
    fig.update_traces(marker_size=12, textposition='middle right')
    
    for i, row in plot_df.iterrows():
        fig.add_shape(
            type='line',
            x0=0, y0=row['Employee Name'],
            x1=row['Utilization %'], y1=row['Employee Name'],
            line=dict(color='lightgrey', width=1)
        )
        
    fig.update_layout(
        yaxis_title=None, 
        xaxis_range=[0, 115], 
        showlegend=False,
        margin=dict(l=20, r=20, t=40, b=20)
    )
    return fig

def plot_utilization_rate_scatter(df, capacity_mins=None, colors=None):
    """
    Scatter version (no lines) - Real utilization rate (Billable / Capacity).
    """
    if capacity_mins:
        # Utilization based on Capacity
        grouped = df.groupby('Employee Name').apply(
            lambda x: x[x['Is_Billable']]['Work Time (Mins)'].sum() / capacity_mins * 100,
            include_groups=False
        ).sort_values(ascending=False)
        title_text = f"Utilization Scorecard - Scatter (Target: {capacity_mins/60:.1f} hrs)"
    else:
        # Old Logic
        grouped = df.groupby('Employee Name').apply(
            lambda x: x[x['Is_Billable']]['Work Time (Mins)'].sum() / x['Work Time (Mins)'].sum() * 100 if x['Work Time (Mins)'].sum() > 0 else 0,
            include_groups=False
        ).sort_values(ascending=False)
        title_text = "Utilization Rate - Scatter (Billable Time %)"
    
    # Prepare DF for Plotly
    plot_df = grouped.reset_index(name='Utilization %')
    
    fig = px.scatter(plot_df, x='Utilization %', y='Employee Name',
                     title=title_text,
                     text=plot_df['Utilization %'].apply(lambda x: f"{x:.1f}%"),
                     color='Utilization %',
                     color_continuous_scale='Teal')
    
    fig.update_traces(marker_size=15, textposition='middle right')
        
    fig.update_layout(
        yaxis_title=None, 
        xaxis_range=[0, 115], 
        showlegend=False,
        margin=dict(l=20, r=20, t=40, b=20)
    )
    return fig

# Keep original function name for backward compatibility
def plot_utilization_rate(df, capacity_mins=None, colors=None):
    """Default to lollipop version"""
    return plot_utilization_rate_lollipop(df, capacity_mins, colors)

def plot_billable_vs_non_billable(df, colors=None):
    """
    Stacked bar chart of Billable vs Non-Billable.
    """
    grouped = df.groupby(['Employee Name', 'Is_Billable'])['Work Time (Mins)'].sum().reset_index()
    grouped['Type'] = grouped['Is_Billable'].map({True: 'Billable (Training/Assessments)', False: 'Non-Billable (Admin/Travel/Mtgs)'})
    
    # Convert to Hours
    grouped['Hours'] = (grouped['Work Time (Mins)'] / 60).round(1)
    
    fig = px.bar(grouped, x='Hours', y='Employee Name', color='Type', 
                 orientation='h', 
                 title="Billable vs Non-Billable Time Breakdown (Hours)",
                 text='Hours',
                 labels={'Hours': 'Hours', 'Employee Name': 'Trainer'},
                 color_discrete_sequence=colors if colors else ['#B3E5E5', '#D4EBF7'])  # Very Light Teal, Very Light Blue
    fig.update_traces(textposition='auto')
    return fig

def get_daily_avg_trend(df):
    """
    Line chart of average minutes per day across all trainers (or filtered).
    """
    # Group by Date and Employee, calculate total mins/day per employee
    daily_sums = df.groupby(['Date_Obj', 'Employee Name'])['Work Time (Mins)'].sum().reset_index()
    # Average across employees for that day
    daily_system_avg = daily_sums.groupby('Date_Obj')['Work Time (Mins)'].mean().reset_index()
    
    fig = px.line(daily_system_avg, x='Date_Obj', y='Work Time (Mins)', 
                  title="Team Average Daily Productive Minutes",
                  markers=True)
    return fig
