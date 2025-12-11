import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

def plot_attendance_heatmap(df):
    """
    Heatmap of Present (P), Leave (L), WO.
    We need a pivot table: Index=Employee, Columns=Date, Value=Attendance Code.
    """
    # We need strictly 1 status per day per employee.
    # The 'Attendance' field was extracted per task, but it should be same for the day.
    # We take the first non-null attendance status for that day/employee.
    
    # Calendar Grid Heatmap
    # X-Axis = Week Number (or Start Date of Week), Y-Axis = Day of Week
    
    # Ensure necessary columns
    if 'Week' not in df.columns or 'DayOfWeek' not in df.columns:
        df['Week'] = df['Date_Obj'].dt.isocalendar().week
        df['DayOfWeek'] = df['Date_Obj'].dt.day_name()
    
    # Filter unique daily status per employee (assuming single employee df passed usually, or avg? 
    # Usually this plot is for single trainer in Tab 5, but if passed multiple, it breaks.
    # The existing function grouping by ['Employee Name', 'Date_Obj'] suggests multiple support but heatmap requires 2D.
    # If multiple employees, we can't do a single calendar grid easily. 
    # Let's assume this is primarily for the Individual View (Tab 5). 
    # If used in Tab 1, we might need a different approach. But Tab 1 uses SUMMARY metrics.
    # Let's optimize for Single Trainer view as per request context.
    
    att_df = df.groupby('Date_Obj').first().reset_index() # Take first entry per date if single trainer
    
    # Map DayOfWeek to specific order for Y-axis
    days_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    att_df['Day_Num'] = att_df['Date_Obj'].dt.dayofweek
    
    # Map Status
    status_map = {'P': 1, 'L': 2, 'WO': 0, 'H': 3, 'A': 4} 
    # 0=WO(Gray), 1=P(Green), 2=L(Orange), 3=H(Blue), 4=A(Red)
    
    att_df['Status_Val'] = att_df['Attendance'].map(lambda x: status_map.get(str(x).strip(), 5))
    
    # Pivot for Heatmap: Index=DayOfWeek, Columns=Week
    pivot_val = att_df.pivot(index='Day_Num', columns='Week', values='Status_Val')
    pivot_text = att_df.pivot(index='Day_Num', columns='Week', values='Attendance')
    
    # Reindex to ensure all days present
    pivot_val = pivot_val.reindex(range(7)).sort_index(ascending=False) # Mon at top or bottom? Standard is Mon top, but Heatmap y=0 is bottom.
    pivot_text = pivot_text.reindex(range(7)).sort_index(ascending=False)
    # Let's flip so Mon is at top
    
    # Actually, let's use explicit y array
    y_labels = days_order[::-1] # Reverse so Monday is top
    
    # We need to map the pivot data correctly to these labels
    # pivot_val index 0 is Monday. If we plot Y=[0..6], 0 is bottom. 
    # So we want Mon (0) at Top (6).
    
    # Let's construct data arrays directly for robustness
    z_data = []
    text_data = []
    for day_idx in range(6, -1, -1): # 6(Sun) to 0(Mon)
        if day_idx in pivot_val.index:
            z_data.append(pivot_val.loc[day_idx].values)
            text_data.append(pivot_text.loc[day_idx].fillna('').values)
        else:
            z_data.append([None]*len(pivot_val.columns))
            text_data.append(['']*len(pivot_val.columns))
            
    # Updated Colors for Heatmap (Stronger, No Pink/Grey/LightYellow)
    # WO=AliceBlue (#F0F8FF), P=ForestGreen (#228B22), L=DarkOrange (#FF8C00), H=RoyalBlue (#4169E1), A=FireBrick (#B22222)
    
    fig = go.Figure(data=go.Heatmap(
        z=z_data,
        x=pivot_val.columns,
        y=y_labels,
        text=text_data,
        texttemplate="%{text}",
        colorscale=[
            [0.0, "#F0F8FF"], # WO (AliceBlue/White-ish)
            [0.2, "#F0F8FF"],
            [0.2, "#90EE90"], # P (Light Green)
            [0.4, "#90EE90"],
            [0.4, "#FFB366"], # L (Light Orange)
            [0.6, "#FFB366"],
            [0.6, "#87CEEB"], # H (Sky Blue)
            [0.8, "#87CEEB"],
            [0.8, "#FF9999"], # A (Light Red)
            [1.0, "#FF9999"]
        ],
        zmin=0, zmax=4,
        xgap=2, ygap=2, # Grid lines
        showscale=False
    ))
    
    fig.update_layout(
        title="Attendance Status (Calendar View)",
        xaxis_title="Week Number",
        yaxis_title="Day of Week",
        height=400
    )
    return fig
    
def plot_leave_rate(df, colors=None):
    # Count days marked 'L' vs total days
    # Aggregation per employee
    att_df = df.groupby(['Employee Name', 'Date_Obj'])['Attendance'].first().reset_index()
    
    counts = att_df.groupby('Employee Name')['Attendance'].value_counts().unstack(fill_value=0)
    
    if 'L' in counts.columns:
        counts['Leave %'] = counts['L'] / counts.sum(axis=1) * 100
        counts.reset_index(inplace=True)
        
        fig = px.bar(counts, x='Employee Name', y='Leave %',
                     title="Availability Gap (Leave %)",
                     labels={'Employee Name': 'Trainer'},
                     text_auto='.1f',
                     color_discrete_sequence=colors if colors else px.colors.qualitative.Pastel)
        return fig
    else:
        return None
