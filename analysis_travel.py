import pandas as pd
import plotly.express as px

def analyze_travel_efficiency(df, colors=None):
    """
    Scatter plot: Mobility (Travel) vs Onsite Delivery Efficiency.
    Excludes Online delivery from the Y-axis.
    Bubble Size = Total Worked Days.
    """
    # Identify Travel
    travel_keywords = ['Travel', 'Travelling']
    training_keywords = ['Training', 'Session', 'Class']
    
    def is_travel(cat):
        return any(k.lower() in str(cat).lower() for k in travel_keywords)
        
    def is_onsite_delivery(cat):
        # Must be training AND NOT Online
        cat_str = str(cat).lower()
        is_tr = any(k.lower() in cat_str for k in training_keywords)
        is_online = 'online' in cat_str
        return is_tr and not is_online
    
    # Calculate totals per employee
    grouped = df.groupby('Employee Name').apply(
        lambda x: pd.Series({
            'Travel Mins': x[x['Activity Category'].apply(is_travel)]['Work Time (Mins)'].sum(),
            'Delivery Mins': x[x['Activity Category'].apply(is_onsite_delivery)]['Work Time (Mins)'].sum(),
            'Total Worked Days': x['Date_Obj'].nunique() if 'Date_Obj' in x.columns else x['Date'].nunique()
        })
    ).reset_index()
    
    # Convert to Hours
    grouped['Travel Hours'] = (grouped['Travel Mins'] / 60).round(1)
    grouped['Delivery Hours'] = (grouped['Delivery Mins'] / 60).round(1)
    
    # Calculate Efficiency % (Delivery / (Delivery + Travel))
    grouped['Total Mobile Hours'] = grouped['Travel Hours'] + grouped['Delivery Hours']
    grouped['Efficiency'] = grouped.apply(lambda x: (x['Delivery Hours'] / x['Total Mobile Hours'] * 100) if x['Total Mobile Hours'] > 0 else 0, axis=1).round(1)
    grouped['Eff. Label'] = grouped['Efficiency'].astype(str) + "%"

    # Scatter plot
    fig = px.scatter(grouped, x='Travel Hours', y='Delivery Hours', 
                     size='Total Worked Days', hover_name='Employee Name',
                     text='Eff. Label',
                     title="Onsite Mobility Efficiency (% of Time Spent Delivering)",
                     labels={'Employee Name': 'Trainer', 'Travel Hours': 'Travel (Hours)', 'Delivery Hours': 'Onsite Delivery (Hours)'},
                     color='Employee Name',
                     color_discrete_sequence=colors if colors else px.colors.qualitative.Pastel)
    
    fig.update_traces(textposition='top center')
    fig.update_layout(margin=dict(l=20, r=20, t=40, b=20))
    return fig

def plot_travel_bar(df, colors=None):
    travel_keywords = ['Travel', 'Travelling']
    travel_df = df[df['Activity Category'].apply(lambda x: any(k.lower() in str(x).lower() for k in travel_keywords))]
    
    grouped = travel_df.groupby('Employee Name')['Work Time (Mins)'].sum().sort_values(ascending=False).reset_index()
    grouped['Hours'] = (grouped['Work Time (Mins)'] / 60).round(1)
    
    fig = px.bar(grouped, x='Hours', y='Employee Name', orientation='h',
                 title="Total Mobility/Travel by Trainer (Hours)",
                 labels={'Employee Name': 'Trainer', 'Hours': 'Hours'},
                 text_auto='.1f',
                 color_discrete_sequence=colors if colors else px.colors.qualitative.Pastel)
    fig.update_layout(margin=dict(l=20, r=20, t=40, b=20))
    return fig
