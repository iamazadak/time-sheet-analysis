import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import data_processor
import analysis_productivity
import analysis_activities
import analysis_training
import analysis_travel
import analysis_location
import analysis_attendance
import analysis_trends
import pdf_generator

# Page Config
st.set_page_config(page_title="Team Productivity & Insights", layout="wide", page_icon="📊")

# Title and Style
st.title("📊 Timesheet & Productivity Analytics Dashboard")
st.markdown("""
<style>
    .metric-card {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)

# 1. Load Data
@st.cache_data
def load_data(file):
    return data_processor.load_and_clean_data(file)

# Sidebar - File Upload
st.sidebar.header("📁 Upload Data")
uploaded_file = st.sidebar.file_uploader("Upload Timesheet CSV", type=['csv'], help="Upload your timesheet CSV file to begin analysis")

# Check if data is loaded
data_loaded = False
df = None

if uploaded_file is not None:
    # Load uploaded file
    df, err = load_data(uploaded_file)
    if err:
        st.sidebar.error(err)
        st.error(f"❌ Error loading file: {err}")
        st.info("Please upload a valid CSV file with the required columns.")
        st.stop()
    else:
        st.sidebar.success(f"✅ File loaded successfully!")
        data_loaded = True
else:
    # Show welcome screen
    st.markdown("""
    ## 👋 Welcome to Timesheet & Productivity Analytics Dashboard
    
    ### 📊 Get Started
    
    To begin analyzing your timesheet data:
    
    1. **Upload your CSV file** using the sidebar uploader
    2. Or use the **sample data** button below to explore features
    
    ### 📋 Required CSV Columns
    
    Your CSV file should include:
    - `Date` - Date of activity
    - `Employee Name` - Trainer/employee identifier
    - `Activity Category` - Type of activity
    - `Work Time (Mins)` - Duration in minutes
    - `Location` - Work location
    - `Attendance` - Attendance status (P/L/WO/H/A)
    
    ### ✨ Features You'll Access
    
    - **Executive Dashboard** - KPIs and high-level metrics
    - **Deep Dive Analysis** - Detailed productivity insights
    - **Trainer 360 Profile** - Individual performance analysis
    - **Raw Data Explorer** - Filter and export data
    - **PDF Reports** - Customizable report generation
    """)
    
    # Option to load sample data
    if st.button("📂 Load Sample Data", type="primary", use_container_width=True):
        default_path = "Time-sheet_2025 - NOV'25.csv"
        try:
            df, err = load_data(default_path)
            if err:
                st.error(f"Could not load sample file: {err}")
                st.stop()
            else:
                st.sidebar.success(f"✅ Loaded sample: {default_path}")
                data_loaded = True
                st.rerun()
        except Exception as e:
            st.error(f"Sample data not found: {e}")
            st.info("Please upload your own CSV file to continue.")
            st.stop()
    
    st.stop()

# === DATA IS LOADED - SHOW ALL FEATURES ===

# Sidebar: Filters
st.sidebar.divider()
st.sidebar.header("🔍 Filters")

dates = sorted(df['Date_Obj'].dropna().unique())
if not dates:
    st.error("No valid dates found in data.")
    st.stop()
    
min_date, max_date = dates[0], dates[-1]

start_date, end_date = st.sidebar.date_input(
    "Date Range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)

locations = sorted(df['Location'].dropna().unique())
sel_locations = st.sidebar.multiselect("Select Location", locations, default=locations)

employees = sorted(df['Employee Name'].dropna().unique())
sel_employees = st.sidebar.multiselect("Select Trainers", employees, default=employees)

st.sidebar.divider()
st.sidebar.header("⚙️ Configuration")
working_days = st.sidebar.number_input("Working Days (in Range/Month)", min_value=1, max_value=31, value=22, step=1)
working_hours = st.sidebar.number_input("Daily Working Hours", min_value=1, max_value=12, value=8, step=1)

st.sidebar.divider()
st.sidebar.header("📄 PDF Export Options")

# Page Size Selection
page_size = st.sidebar.selectbox(
    "Page Size",
    options=['A0', 'A1', 'A2', 'A3', 'A4', 'A5', 'A6', 'Letter', 'Legal'],
    index=4  # Default to A4
)

# Page Orientation
page_orientation = st.sidebar.radio(
    "Page Orientation",
    options=['Portrait', 'Landscape'],
    horizontal=True
)

# Cover Page Option
include_cover = st.sidebar.checkbox("Include Cover Page", value=True)

# Table Inclusion Options
st.sidebar.markdown("**Include Tables:**")
include_raw_data = st.sidebar.checkbox("Raw Data Table", value=False)
include_summary_table = st.sidebar.checkbox("Summary Metrics Table", value=True)
include_trainer_table = st.sidebar.checkbox("Trainer Performance Table", value=True)

# Global Color Theme
pastel_colors = px.colors.qualitative.Bold 
cust_pastel = ['#008B8B', '#4169E1', '#228B22', '#DAA520', '#800080', '#CC5500', '#20B2AA', '#4682B4', '#556B2F']

state_params = {
    'working_days': working_days,
    'working_hours': working_hours,
    'capacity_mins': working_days * working_hours * 60,
    'colors': cust_pastel
}

# Filter by Date and Selections
df_filtered = df[(df['Date_Obj'].dt.date >= start_date) & (df['Date_Obj'].dt.date <= end_date)]

if sel_locations:
    df_filtered = df_filtered[df_filtered['Location'].isin(sel_locations)]

if sel_employees:
    df_filtered = df_filtered[df_filtered['Employee Name'].isin(sel_employees)]

if df_filtered.empty:
    st.warning("No data matches the selected filters.")
    st.stop()

# PDF Generation Button
st.sidebar.divider()
if st.sidebar.button("📥 Generate PDF Report", type="primary", use_container_width=True):
    with st.spinner("Generating PDF Report..."):
        try:
            # Collect metrics
            total_hours = df_filtered['Work Time (Mins)'].sum() / 60
            training_hours = analysis_training.get_training_metrics(df_filtered)[0].sum() / 60
            active_trainers = df_filtered['Employee Name'].nunique()
            avg_utilization = (training_hours / total_hours * 100) if total_hours > 0 else 0
            
            metrics = {
                'Total Logged Hours': f"{total_hours:,.1f} h",
                'Total Training Hours': f"{training_hours:,.1f} h",
                'Active Trainers': active_trainers,
                'Average Training Utilization': f"{avg_utilization:.1f}%",
                'Date Range': f"{start_date} to {end_date}",
                'Locations': ', '.join(sel_locations) if sel_locations else 'All',
                'Trainers': ', '.join(sel_employees) if len(sel_employees) <= 5 else f"{len(sel_employees)} trainers"
            }
            
            # Collect charts
            charts = []
            
            # Utilization chart
            charts.append({
                'fig': analysis_productivity.plot_utilization_rate_lollipop(df_filtered, capacity_mins=state_params['capacity_mins'], colors=state_params['colors']),
                'title': 'Utilization Score by Trainer'
            })
            
            # Activity treemap
            activity_color_map = analysis_activities.get_activity_color_map(df_filtered)
            charts.append({
                'fig': analysis_activities.plot_activity_treemap(df_filtered, color_map=activity_color_map),
                'title': 'Time Investment by Activity'
            })
            
            # Weekly trends
            charts.append({
                'fig': analysis_trends.get_weekly_summary(df_filtered, colors=state_params['colors']),
                'title': 'Weekly Work Trends'
            })
            
            # Billable vs Non-billable
            charts.append({
                'fig': analysis_productivity.plot_billable_vs_non_billable(df_filtered, colors=state_params['colors']),
                'title': 'Billable vs Non-Billable Hours'
            })
            
            # Prepare tables based on checkbox selections
            tables_to_include = []
            
            # Summary Metrics Table
            if include_summary_table:
                summary_df = pd.DataFrame({
                    'Metric': list(metrics.keys()),
                    'Value': list(metrics.values())
                })
                tables_to_include.append({
                    'name': 'summary_metrics',
                    'df': summary_df,
                    'title': 'Summary Metrics'
                })
            
            # Trainer Performance Table
            if include_trainer_table:
                # Create trainer performance summary
                trainer_stats = []
                for trainer in df_filtered['Employee Name'].unique():
                    trainer_df = df_filtered[df_filtered['Employee Name'] == trainer]
                    total_mins = trainer_df['Work Time (Mins)'].sum()
                    
                    # Training hours
                    training_keywords = ['Training', 'Session', 'Delivery', 'Facilitation']
                    train_mins = trainer_df[trainer_df['Activity Category'].apply(
                        lambda x: any(k.lower() in str(x).lower() for k in training_keywords)
                    )]['Work Time (Mins)'].sum()
                    
                    # Billable hours
                    billable_mins = trainer_df[trainer_df['Is_Billable']]['Work Time (Mins)'].sum()
                    
                    # Utilization
                    capacity_mins = state_params['capacity_mins']
                    if capacity_mins:
                        util_score = (billable_mins / capacity_mins * 100)
                    else:
                        util_score = (billable_mins / total_mins * 100) if total_mins > 0 else 0
                    
                    trainer_stats.append({
                        'Trainer': trainer,
                        'Total Hours': f"{total_mins/60:.1f}",
                        'Training Hours': f"{train_mins/60:.1f}",
                        'Billable Hours': f"{billable_mins/60:.1f}",
                        'Utilization %': f"{util_score:.1f}%"
                    })
                
                trainer_perf_df = pd.DataFrame(trainer_stats)
                tables_to_include.append({
                    'name': 'trainer_performance',
                    'df': trainer_perf_df,
                    'title': 'Trainer Performance Summary'
                })
            
            # Raw Data Table
            if include_raw_data:
                # Select key columns for raw data
                raw_data_cols = ['Date', 'Employee Name', 'Activity Category', 'Work Time (Mins)', 
                                'Location', 'Attendance', 'Is_Billable']
                available_cols = [col for col in raw_data_cols if col in df_filtered.columns]
                raw_df = df_filtered[available_cols].copy()
                
                tables_to_include.append({
                    'name': 'raw_data',
                    'df': raw_df,
                    'title': 'Raw Timesheet Data'
                })
            
            # Configure report
            pdf_config = {
                'page_size': page_size,
                'orientation': page_orientation,
                'include_cover': include_cover,
                'tables': tables_to_include
            }
                
            # Generate PDF
            pdf_buffer = pdf_generator.create_timesheet_report(
                df=None,  # Pass tables separately now
                metrics=metrics,
                charts=charts,
                config=pdf_config
            )
            
            # Download button
            st.sidebar.download_button(
                label="⬇️ Download PDF",
                data=pdf_buffer,
                file_name=f"timesheet_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                mime="application/pdf",
                use_container_width=True
            )
            
            st.sidebar.success("✅ PDF Generated Successfully!")
            
        except Exception as e:
            st.sidebar.error(f"Error generating PDF: {str(e)}")
            st.sidebar.exception(e)

# --- TABS ---
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🚀 Executive Dashboard", 
    "🔍 Deep Dive Analysis", 
    "👤 Trainer 360",
    "💾 Raw Data",
    "📘 Metric Definitions"
])

# --- TAB 1: EXECUTIVE DASHBOARD ---
with tab1:
    st.header("Executive Summary")
    
    # Top Metrics
    c1, c2, c3, c4 = st.columns(4)
    total_hours = df_filtered['Work Time (Mins)'].sum() / 60
    training_hours = analysis_training.get_training_metrics(df_filtered)[0].sum() / 60
    active_trainers = df_filtered['Employee Name'].nunique()
    avg_utilization = (training_hours / total_hours * 100) if total_hours > 0 else 0
    
    # Calculate Capacity/Target
    target_hours_person = state_params['capacity_mins'] / 60 if state_params['capacity_mins'] else 0
    total_capacity = target_hours_person * active_trainers
    
    # Display Target Context
    if target_hours_person > 0:
        st.info(f"🎯 **Ideal Target:** {target_hours_person:.1f} Hours / Trainer (Total Capacity: {total_capacity:,.0f} Hours)")
    else:
        st.info("🎯 **Target:** Not Configured (Set Working Days in Sidebar)")
    
    c1.metric("Total Logged Hours", f"{total_hours:,.1f} h", delta=f"{total_hours - total_capacity:,.1f} h vs Capacity" if target_hours_person > 0 else None)
    c2.metric("Total Training Hours", f"{training_hours:,.1f} h")
    c3.metric("Active Trainers", active_trainers)
    c4.metric("Avg Training Util %", f"{avg_utilization:.1f}%")
    
    st.divider()
    
    
    # Utilization Scorecard
    st.subheader("Leaderboard: Utilization Score")
    st.plotly_chart(analysis_productivity.plot_utilization_rate_lollipop(df_filtered, capacity_mins=state_params['capacity_mins'], colors=state_params['colors']), use_container_width=True, key="tab1_util")
    
    
    st.divider()
    
    st.divider()
    
    # Generate Consistent Color Map for Activity Plots
    activity_color_map = analysis_activities.get_activity_color_map(df_filtered)
    
    # Treemap (Activity Distribution)
    st.subheader("Total Time Investment by Activity")
    st.plotly_chart(analysis_activities.plot_activity_treemap(df_filtered, color_map=activity_color_map), use_container_width=True, key="tab1_tree")
    
    st.divider()
    
    # Consolidated High-Level View
    st.subheader("Weekly Work Trends")
    fig_trend = analysis_trends.get_weekly_summary(df_filtered, colors=state_params['colors'])
    st.plotly_chart(fig_trend, use_container_width=True, key="tab1_trend")

# --- TAB 2: DEEP DIVE ANALYSIS (Consolidated) ---
with tab2:
    st.header("Productivity, Activities & Operations Deep Dive")
    
    # SECTION 1: PRODUCTIVITY
    st.success("### 1️⃣ Productivity & Utilization")
    
    # Scorecard moved to Exec Dashboard
    pass
    
    c1, c2 = st.columns(2)
    with c1:
        # Fixed total_mins scope issue
        total_mins_series = df_filtered.groupby('Employee Name')['Work Time (Mins)'].sum().sort_values(ascending=False)
        st.plotly_chart(analysis_productivity.plot_total_logged_minutes(total_mins_series, colors=state_params['colors']), use_container_width=True, key="tab2_focus")
    with c2:
        st.plotly_chart(analysis_productivity.plot_billable_vs_non_billable(df_filtered, colors=state_params['colors']), use_container_width=True, key="tab2_billable")
        
    st.divider()
    
    # SECTION 2: ACTIVITIES & TRAINING
    st.info("### 2️⃣ Training & Activity Breakdown")
    
    st.caption("Activity Distribution (Hours)")
    st.plotly_chart(analysis_activities.plot_activity_stacked_bar(df_filtered, color_map=activity_color_map), use_container_width=True, key="tab3_stacked")

    c3, c4 = st.columns(2)
    tr_mins, tr_sess, tr_df = analysis_training.get_training_metrics(df_filtered)
    with c3:
        st.plotly_chart(analysis_training.plot_training_leaderboard(tr_mins, colors=state_params['colors']), use_container_width=True, key="tab3_leader")
    with c4:
        st.plotly_chart(analysis_training.plot_online_vs_offline(tr_df, colors=state_params['colors']), use_container_width=True, key="tab3_mode")
    
    st.divider()
    
    # SECTION 3: OPERATIONS & TRAVEL
    st.warning("### 3️⃣ Operations, Travel & Locations")
    

    
    c5, c6 = st.columns(2)
    with c5:
        st.plotly_chart(analysis_travel.analyze_travel_efficiency(df_filtered, colors=state_params['colors']), use_container_width=True, key="tab4_eff")
    with c6:
        st.plotly_chart(analysis_location.plot_location_performance(df_filtered, colors=state_params['colors']), use_container_width=True, key="tab4_loc")

# --- TAB 3: TRAINER 360 ---
with tab3:
    st.header("Individual Trainer Profile")
    
    selected_trainer = st.selectbox("Select Trainer Profile", employees)
    
    if selected_trainer:
        trainer_df = df[df['Employee Name'] == selected_trainer].copy()
        
        # Calculate KPIs directly
        total_mins = trainer_df['Work Time (Mins)'].sum()
        training_keywords = ['Training', 'Session', 'Delivery', 'Facilitation']
        travel_keywords = ['Travel', 'Travelling']
        
        def check_k(cat, keywords):
            return any(k.lower() in str(cat).lower() for k in keywords)

        train_mins = trainer_df[trainer_df['Activity Category'].apply(lambda x: check_k(x, training_keywords))]['Work Time (Mins)'].sum()
        travel_mins = trainer_df[trainer_df['Activity Category'].apply(lambda x: check_k(x, travel_keywords))]['Work Time (Mins)'].sum()
        billable_mins = trainer_df[trainer_df['Is_Billable']]['Work Time (Mins)'].sum()
        
        # Calculate Utilization
        capacity_mins = state_params['capacity_mins']
        if capacity_mins:
            util_score = (billable_mins / capacity_mins * 100)
        else:
            util_score = (billable_mins / total_mins * 100) if total_mins > 0 else 0
            
        target_hours = capacity_mins / 60 if capacity_mins else 0
        
        # Calculate Attendance Metrics (Presence vs Total Days)
        total_days = trainer_df['Date_Obj'].nunique()
        leave_days = trainer_df[trainer_df['Attendance'] == 'L']['Date_Obj'].nunique()
        # Assume 'P' or 'WO' or any check-in implies presence relative to leave? 
        # Usually Attendance Rate = 100 - Leave Rate? Or specifically 'P' days.
        # Let's use explicit 'P' count for Attendance Rate.
        present_days = trainer_df[trainer_df['Attendance'] == 'P']['Date_Obj'].nunique()
        
        leave_rate = (leave_days / total_days * 100) if total_days > 0 else 0
        p_attendance = (present_days / total_days * 100) if total_days > 0 else 0

        c1, c2, c3, c4, c5, c6, c7 = st.columns(7)
        c1.metric("Total Hours", f"{total_mins/60:.1f}", delta=f"{(total_mins/60) - target_hours:.1f} h" if target_hours > 0 else None)
        c2.metric("Training Hours", f"{train_mins/60:.1f}")
        c3.metric("Travel Hours", f"{travel_mins/60:.1f}")
        c4.metric("Util Score", f"{util_score:.1f}%")
        c5.metric("Target", f"{target_hours:.1f} h")
        c6.metric("Attendance", f"{p_attendance:.1f}%")
        c7.metric("Leave Rate", f"{leave_rate:.1f}%")
        
        st.divider()
        
        # Side-by-Side Layout
        col_a, col_b = st.columns(2)
        
        with col_a:
            st.subheader(f"Activity Breakdown")
            # Use global map for consistency even in filtered trainer view
            fig_act = analysis_activities.plot_activity_bubble(trainer_df, color_map=activity_color_map)
            st.plotly_chart(fig_act, use_container_width=True, key="tab3_bubble")
            
        with col_b:
            st.subheader("Attendance Calendar")
            st.plotly_chart(analysis_attendance.plot_attendance_heatmap(trainer_df), use_container_width=True, key="tab3_heat")

# --- TAB 4: RAW DATA ---
with tab4:
    st.header("Raw Data")
    
    display_df = df_filtered.copy()
    
    # Enhance Data for Filtering
    if 'Date_Obj' in display_df.columns:
        display_df['Week'] = display_df['Date_Obj'].dt.isocalendar().week
        display_df['DayOfWeek'] = display_df['Date_Obj'].dt.day_name()
    
    # Filter Columns
    fc1, fc2, fc3, fc4 = st.columns(4)
    
    with fc1:
        # Employee Filter
        all_emps = sorted(display_df['Employee Name'].unique())
        sel_emps = st.multiselect("Employee", all_emps)
    
    with fc2:
        # Category Filter
        all_cats = sorted(display_df['Activity Category'].astype(str).unique())
        sel_cats = st.multiselect("Category", all_cats)
        
    with fc3:
        # Week Filter
        if 'Week' in display_df.columns:
            all_weeks = sorted(display_df['Week'].unique())
            sel_weeks = st.multiselect("Week", all_weeks)
        else:
            sel_weeks = []
            
    with fc4:
        # DayOfWeek Filter
        if 'DayOfWeek' in display_df.columns:
            days_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
            all_days = sorted(display_df['DayOfWeek'].unique(), key=lambda x: days_order.index(x) if x in days_order else 99)
            sel_days = st.multiselect("Day Of Week", all_days)
        else:
            sel_days = []
            
    # Apply Filters
    if sel_emps:
        display_df = display_df[display_df['Employee Name'].isin(sel_emps)]
    if sel_cats:
        display_df = display_df[display_df['Activity Category'].isin(sel_cats)]
    if sel_weeks:
        display_df = display_df[display_df['Week'].isin(sel_weeks)]
    if sel_days:
        display_df = display_df[display_df['DayOfWeek'].isin(sel_days)]
        
    st.dataframe(display_df, use_container_width=True)
    
    csv = display_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="Download Cleaned Data as CSV",
        data=csv,
        file_name='cleaned_timesheet_data.csv',
        mime='text/csv',
    )

    st.divider()
    
    st.subheader("🚩 Red Flags & Anomalies")
    anomalies = analysis_trends.detect_anomalies(df_filtered)
    if not anomalies.empty:
        # Filter by Trainer
        anom_trainers = sorted(anomalies['Employee Name'].unique())
        sel_anom_trainers = st.multiselect("Filter Anomalies by Trainer", anom_trainers)
        
        if sel_anom_trainers:
            anomalies = anomalies[anomalies['Employee Name'].isin(sel_anom_trainers)]
            
        st.dataframe(anomalies, use_container_width=True)
    else:
        st.success("No major data anomalies detected.")

# --- TAB 5: DEFINITIONS ---
with tab5:
    st.header("📘 Metric Definitions & Formulas")
    
    st.markdown("""
    ### 1. Productivity Metrics
    
    #### Total Logged Hours
    **Formula:**  
    $$ \\text{Total Hours} = \\frac{\\sum \\text{Work Time (Mins)}}{60} $$
    
    **Physical Significance:**  
    Represents the total time investment by a trainer across all activities. This is the baseline metric for workload assessment and capacity planning.
    
    #### Utilization Score
    **Formula:**  
    $$ \\text{Utilization \\%} = \\frac{\\text{Billable Minutes}}{\\text{Capacity Minutes}} \\times 100 $$
    
    where: $$ \\text{Capacity Minutes} = \\text{Working Days} \\times \\text{Daily Working Hours} \\times 60 $$
    
    **Physical Significance:**  
    Measures how effectively a trainer's time is being used for revenue-generating activities (training delivery). Higher utilization (70-85%) indicates optimal productivity, while very high (>90%) may signal burnout risk, and low (<50%) suggests underutilization or excessive non-billable work.
    
    ---
    
    ### 2. Training Metrics
    
    #### Training Hours Delivered
    **Formula:**  
    $$ \\text{Training Hours} = \\frac{\\sum \\text{Training Activity Minutes}}{60} $$
    
    Training activities identified by keywords: 'Training', 'Session', 'Class', 'Delivery', 'Facilitation'
    
    **Physical Significance:**  
    Core deliverable metric showing actual training output. Critical for assessing trainer productivity and calculating training ROI.
    
    #### Mode of Delivery Distribution
    **Categorization Logic:**
    - **Online**: Activity Category contains "Online"
    - **Offline/Onsite**: Activity Category contains "Offline" or "Onsite"
    
    **Physical Significance:**  
    Helps understand delivery channel mix, cost implications (onsite requires travel), and trainer versatility. Essential for hybrid training strategy planning.
    
    ---
    
    ### 3. Mobility & Efficiency Metrics
    
    #### Onsite Mobility Efficiency
    **Formula:**  
    $$ \\text{Efficiency \\%} = \\frac{\\text{Onsite Delivery Hours}}{\\text{Onsite Delivery Hours + Travel Hours}} \\times 100 $$
    
    **Physical Significance:**  
    Indicates what percentage of "road time" is spent actually delivering value vs. commuting. Higher efficiency (>60%) means better travel planning and route optimization. Low efficiency (<40%) suggests need for better scheduling or remote delivery options.
    
    #### Travel Hours
    **Formula:**  
    $$ \\text{Travel Hours} = \\frac{\\sum \\text{Travel Activity Minutes}}{60} $$
    
    Travel activities identified by keywords: 'Travel', 'Travelling'
    
    **Physical Significance:**  
    Non-billable overhead that impacts cost and trainer fatigue. Should be minimized through strategic scheduling and location clustering.
    
    ---
    
    ### 4. Attendance Metrics
    
    #### Attendance Rate
    **Formula:**  
    $$ \\text{Attendance Rate \\%} = \\frac{\\text{Days Marked Present (P)}}{\\text{Total Working Days}} \\times 100 $$
    
    **Physical Significance:**  
    Measures trainer availability and reliability. Industry standard is >95%. Lower rates may indicate health issues, engagement problems, or data quality issues.
    
    #### Leave Rate
    **Formula:**  
    $$ \\text{Leave Rate \\%} = \\frac{\\text{Days Marked as Leave (L)}}{\\text{Total Working Days}} \\times 100 $$
    
    **Physical Significance:**  
    Tracks planned absences. Typical range is 5-10% annually. Unusually high rates warrant investigation for burnout or personal issues.
    
    #### Attendance Codes (Trainer 360)
    - **P**: Present (Logged hours > 0)
    - **L**: Leave (Planned absence)
    - **WO**: Week Off (Weekend/Scheduled off)
    - **H**: Holiday (Public holiday)
    - **A**: Absent (Unplanned absence - work day with 0 hours and no leave marked)
    
    ---
    
    ### 5. Activity Distribution Metrics
    
    #### Priority Compliance
    **Categorization:**  
    Tasks grouped by 'Task Priority' field: High, Medium, Low
    
    **Physical Significance:**  
    Shows whether trainers are focusing on high-impact activities. Ideal distribution: 40-50% High priority, 30-40% Medium, 10-20% Low. Too many low-priority tasks suggest poor time management or unclear priorities.
    
    #### Activity Category Breakdown
    **Measurement:**  
    Time distribution across different activity types (Training, Admin, Travel, Meetings, etc.)
    
    **Physical Significance:**  
    Reveals how trainer time is actually spent vs. intended role. Excessive admin time (>20%) or meeting time (>15%) indicates process inefficiencies.
    
    ---
    
    ### 6. Anomaly Detection (Red Flags)
    
    #### Long Work Day
    **Threshold:** > 10 Hours logged in a single day
    
    **Physical Significance:**  
    Potential burnout indicator or data entry error. Consistent long days require intervention for work-life balance.
    
    #### Short Work Day
    **Threshold:** < 4 Hours logged on a working day (non-leave)
    
    **Physical Significance:**  
    May indicate partial day work, data entry gaps, or underutilization. Requires investigation.
    
    #### Weekend Work
    **Detection:** Activity logged on Saturday/Sunday
    
    **Physical Significance:**  
    Indicates work-life balance issues or urgent project demands. Should be exceptional, not routine.
    
    #### Zero Minutes Logged
    **Detection:** Work Time = 0 but Description exists
    
    **Physical Significance:**  
    Data quality issue - activity recorded but duration missing. Affects all time-based metrics.
    
    ---
    
    ### 7. Regional Performance
    
    #### Location-Based Metrics
    **Measurement:**  
    Work hours and activity distribution grouped by 'Location' field
    
    **Physical Significance:**  
    Identifies high-demand regions, resource allocation needs, and potential expansion opportunities. Helps optimize trainer deployment.
    
    ---
    
    ### 8. Trend Analysis
    
    #### Weekly Work Trends
    **Measurement:**  
    Time-series analysis of work hours by week
    
    **Physical Significance:**  
    Reveals seasonal patterns, workload fluctuations, and capacity planning needs. Helps predict resource requirements and identify unsustainable work patterns.
    
    ---
    
    ### 9. Categorization Logic
    
    #### Billable Activities
    Keywords: 'Training', 'Session Details', 'Assessments', 'Delivery', 'Facilitation', 'Class'
    
    **Physical Significance:**  
    Revenue-generating activities that justify trainer costs and drive business value.
    
    #### Non-Billable Activities
    Categories: Admin work, Travel, Meetings, Sync-ups, Planning
    
    **Physical Significance:**  
    Necessary overhead but should be minimized. Target: <30% of total time.
    """)
