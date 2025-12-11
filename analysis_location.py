import pandas as pd
import plotly.express as px

def plot_location_performance(df, colors=None):
    """
    Side-by-side comparison of regions.
    Metrics: Total Work Hours, Training Hours, Travel Hours.
    """
    # Aggregate data by Location and broadly categorized activity
    
    def categorize(cat):
        cat = str(cat).lower()
        if 'travel' in cat:
            return 'Travel'
        elif 'training' in cat or 'session' in cat:
            return 'Training'
        elif 'content' in cat:
            return 'Content Creation'
        else:
            return 'Other/Admin'
            
    df['Broad_Category'] = df['Activity Category'].apply(categorize)
    
    grouped = df.groupby(['Location', 'Broad_Category'])['Work Time (Mins)'].sum().reset_index()
    grouped['Hours'] = (grouped['Work Time (Mins)'] / 60).round(1)
    
    fig = px.bar(grouped, x='Location', y='Hours', color='Broad_Category',
                 title="Regional Performance: Activity Distribution (Hours)",
                 labels={'Hours': 'Hours'},
                 barmode='group',
                 text_auto='.1f',
                 color_discrete_sequence=colors if colors else ['#B3E5E5', '#D4EBF7', '#E0F2F7', '#EBF8FB'])  # Very Light Teal/Blue palette
    fig.update_layout(margin=dict(l=20, r=20, t=40, b=20))
    return fig
