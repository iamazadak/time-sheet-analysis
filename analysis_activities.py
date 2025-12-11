import pandas as pd
import plotly.express as px

# Custom Palette: Red + Light Shades (Shared)
custom_palette = [
    '#F97B72', # Light Red (Plotly Bold Red)
    '#85C1E9', # Light Blue
    '#7DCEA0', # Light Green
    '#F7DC6F', # Light Yellow
    '#BB8FCE', # Light Purple
    '#F0B27A', # Light Orange
    '#76D7C4', # Light Teal
    '#D7BDE2'  # Lavender
]

def get_activity_color_map(df):
    """
    Generates a consistent color map based on global Total Hours descending.
    Ensures the top category (e.g. Training) always gets the first color (Red),
    regardless of the specific subset of data being plotted.
    Special handling: "Other Activities" gets gray color.
    """
    # Group by Category and sort by Total Hours Descending
    cat_order = df.groupby('Activity Category')['Work Time (Mins)'].sum().sort_values(ascending=False).index.tolist()
    
    color_map = {}
    for i, cat in enumerate(cat_order):
        # Special case: Assign gray to "Other" activities
        if 'other' in str(cat).lower():
            color_map[cat] = '#B0B0B0'  # Light Gray
        else:
            # Assign color from custom_palette cyclically
            color_map[cat] = custom_palette[i % len(custom_palette)]
        
    return color_map

def plot_activity_stacked_bar(df, color_map=None):
    """
    Stacked Bar Chart replacing Sunburst.
    X=Facilitator, Y=Hours, Color=Activity Category.
    """
    df_clean = df[df['Work Time (Mins)'] > 0].copy()
    grouped = df_clean.groupby(['Employee Name', 'Activity Category'])['Work Time (Mins)'].sum().reset_index()
    grouped['Hours'] = (grouped['Work Time (Mins)'] / 60).round(1)
    
    # If no map provided, generate local one (fallback)
    if color_map is None:
        color_map = get_activity_color_map(df)

    fig = px.bar(grouped, x='Hours', y='Employee Name', color='Activity Category',
                 title="Activity Distribution by Trainer (Hours)",
                 labels={'Employee Name': 'Trainer', 'Hours': 'Time Investment (Hours)'},
                 text_auto=True,
                 orientation='h',
                 # Force order in legend to match ranking for better UX
                 category_orders={'Activity Category': list(color_map.keys())},
                 color_discrete_map=color_map)
    fig.update_layout(margin=dict(l=20, r=20, t=50, b=20))
    return fig

def plot_activity_treemap(df, color_map=None):
    grouped = df.groupby('Activity Category')['Work Time (Mins)'].sum().reset_index()
    grouped['Hours'] = (grouped['Work Time (Mins)'] / 60).round(1)
    
    # If no map provided, generate local one
    if color_map is None:
        color_map = get_activity_color_map(df)
    
    fig = px.treemap(grouped, path=['Activity Category'], values='Hours',
                     title="Total Time Investment by Activity Type (Hours)",
                     color='Activity Category',
                     color_discrete_map=color_map)
    fig.update_traces(textinfo="label+value+percent entry", textposition='middle center')
    fig.update_layout(margin=dict(l=10, r=10, t=40, b=10))
    return fig

def plot_activity_breakdown_bar(df, colors=None):
    grouped = df.groupby('Activity Category')['Work Time (Mins)'].sum().sort_values(ascending=False).reset_index()
    grouped['Hours'] = (grouped['Work Time (Mins)'] / 60).round(1)
    total_hours = grouped['Hours'].sum()
    grouped['%'] = (grouped['Hours'] / total_hours * 100).round(1).astype(str) + '%'
    
    # Using 'Plasma' for safe colors
    
    fig = px.bar(grouped, x='Hours', y='Activity Category',
                 text=grouped.apply(lambda x: f"{x['Hours']}h ({x['%']})", axis=1),
                 orientation='h',
                 title="Detailed Activity Breakdown (Hours & %)",
                 labels={'Activity Category': 'Activity', 'Hours': 'Hours'},
                 color='Hours',
                 color_continuous_scale='Plasma') 
    
    fig.update_traces(textposition='outside')
    fig.update_layout(showlegend=False)
    return fig

def plot_priority_compliance(df, colors=None):
    if 'Task Priority' not in df.columns:
        return None
        
    df_prio = df[df['Task Priority'].notna() & (df['Task Priority'] != '')].copy()
    grouped = df_prio.groupby(['Employee Name', 'Task Priority'])['Work Time (Mins)'].count().reset_index(name='Task Count')
    
    priority_order = {'High': 0, 'Medium': 1, 'Low': 2}
    grouped.sort_values(by='Task Priority', key=lambda x: x.map(priority_order).fillna(3), inplace=True)
    
    # Custom Strong Colors
    prio_colors = {'High': '#DC143C', 'Medium': '#FF8C00', 'Low': '#228B22'} 
    
    # Reverted to Count-based Horizontal Bar (Not 100% Stacked)
    fig = px.bar(grouped, x='Task Count', y='Employee Name', color='Task Priority',
                 orientation='h',
                 title="Priority Compliance (Count of Tasks)",
                 labels={'Employee Name': 'Trainer', 'Task Count': 'Task Count'},
                 text_auto=True,
                 color_discrete_map=prio_colors)
                 
    return fig

def plot_activity_bubble(df, color_map=None):
    """
    Bubble Chart for Activity Breakdown.
    X = Activity Category, Y = Hours, Size = Hours.
    """
    grouped = df.groupby('Activity Category')['Work Time (Mins)'].sum().reset_index()
    grouped['Hours'] = (grouped['Work Time (Mins)'] / 60).round(1)
    
    # Sort for better visual
    grouped = grouped.sort_values('Hours', ascending=False)
    
    # If no map provided, generate local one
    if color_map is None:
        color_map = get_activity_color_map(df)
    
    fig = px.scatter(grouped, x='Activity Category', y='Hours',
                     size='Hours', color='Activity Category',
                     title="Activity Breakdown (Bubble Analysis)",
                     labels={'Hours': 'Hours', 'Activity Category': 'Activity'},
                     text='Hours',
                     size_max=60,
                     color_discrete_map=color_map)
    
    fig.update_traces(textposition='top center')
    fig.update_layout(showlegend=False, height=500, margin=dict(l=20, r=20, t=50, b=20))
    return fig
