# 📊 Timesheet & Productivity Analytics Dashboard

A comprehensive, production-ready Streamlit dashboard for analyzing employee timesheet data with interactive visualizations, advanced analytics, and customizable PDF reporting.

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://time-sheet-analysis-jqwzv9kmthzhbesg4hq5bu.streamlit.app/)

## 🌟 Live Demo

**Access the live application:** [https://time-sheet-analysis-jqwzv9kmthzhbesg4hq5bu.streamlit.app/](https://time-sheet-analysis-jqwzv9kmthzhbesg4hq5bu.streamlit.app/)

## ✨ Key Features

### 📈 Analytics & Dashboards

#### 1. Executive Dashboard
- **Key Performance Indicators (KPIs)**
  - Total Logged Hours with capacity comparison
  - Total Training Hours
  - Active Trainers count
  - Average Training Utilization percentage
- **Utilization Leaderboard** - Interactive lollipop chart showing trainer performance
- **Activity Investment Treemap** - Visual breakdown of time allocation across activities
- **Weekly Work Trends** - Time-series analysis of work patterns

#### 2. Deep Dive Analysis
- **Productivity & Utilization**
  - Total logged minutes by trainer
  - Billable vs Non-Billable hours breakdown
  - Focus time analysis
- **Training & Activity Breakdown**
  - Stacked bar charts for activity distribution
  - Training leaderboard
  - Online vs Offline training mode comparison
- **Operations, Travel & Locations**
  - Travel efficiency metrics
  - Location-based performance analysis

#### 3. Trainer 360 Profile
Individual trainer deep-dive with:
- Total Hours, Training Hours, Travel Hours
- Utilization Score and Target Hours
- Attendance Rate and Leave Rate
- Activity Breakdown (Bubble Chart)
- Attendance Calendar (GitHub-style heatmap)

#### 4. Raw Data Explorer
- **Advanced Filtering**
  - Filter by Employee Name
  - Filter by Activity Category
  - Filter by Week
  - Filter by Day of Week
- **Data Export** - Download filtered data as CSV
- **Anomaly Detection** - Automatic flagging of data issues

#### 5. Metric Definitions
Comprehensive documentation of:
- Productivity metrics formulas
- Training metrics calculations
- Mobility & efficiency metrics
- Attendance metrics
- Anomaly detection thresholds

### 📄 PDF Export Feature

**Comprehensive PDF report generation with customizable options:**

#### Page Configuration
- **Page Sizes**: A0, A1, A2, A3, A4, A5, A6, Letter, Legal
- **Orientation**: Portrait or Landscape
- **Cover Page**: Optional professional cover page with metadata

#### Content Options
- **Summary Metrics Table** - Executive KPIs overview
- **Trainer Performance Table** - Individual trainer statistics with:
  - Total Hours
  - Training Hours
  - Billable Hours
  - Utilization Percentage
- **Raw Data Table** - Filtered timesheet data (up to 100 rows)
- **Charts & Visualizations** - Embedded analytics charts (when available)

#### Export Process
1. Configure filters in sidebar (date range, locations, trainers)
2. Select PDF options (page size, orientation, tables)
3. Click "📥 Generate PDF Report"
4. Download generated PDF with timestamped filename

> **Note**: On Streamlit Cloud, charts display as descriptive text due to server limitations. Full chart images available when running locally with Kaleido installed.

## 🚀 Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Local Setup

1. **Clone the repository**
```bash
git clone https://github.com/iamazadak/time-sheet-analysis.git
cd time-sheet-analysis
```

2. **Create virtual environment**
```bash
python -m venv .venv
```

3. **Activate virtual environment**
```bash
# Windows PowerShell
.\.venv\Scripts\Activate.ps1

# Windows CMD
.\.venv\Scripts\activate.bat

# macOS/Linux
source .venv/bin/activate
```

4. **Install dependencies**
```bash
pip install -r requirements.txt
```

5. **Run the application**
```bash
streamlit run app.py
```

The app will open automatically at `http://localhost:8501`

## 📦 Dependencies

### Core Libraries
- **streamlit** (1.52.1) - Web application framework
- **pandas** (2.3.3) - Data manipulation and analysis
- **plotly** (6.5.0) - Interactive visualizations
- **numpy** (2.3.5) - Numerical computing

### PDF Generation
- **reportlab** (4.4.6) - PDF creation library
- **kaleido** (1.2.0) - Static image export for Plotly (optional for local use)

### Supporting Libraries
- **altair** - Declarative visualization
- **gitpython** - Git integration
- **pillow** - Image processing

See `requirements.txt` for complete dependency list.

## 📁 Project Structure

```
time-sheet-analysis/
├── app.py                      # Main Streamlit application
├── data_processor.py           # Data loading and cleaning utilities
├── pdf_generator.py            # PDF report generation module
├── color_gen.py                # Color palette generator
├── analysis_activities.py      # Activity analysis & visualizations
├── analysis_attendance.py      # Attendance tracking & heatmaps
├── analysis_location.py        # Location-based performance
├── analysis_productivity.py    # Productivity & utilization metrics
├── analysis_training.py        # Training session analytics
├── analysis_travel.py          # Travel efficiency analysis
├── analysis_trends.py          # Trend analysis & anomaly detection
├── Time-sheet_2025 - NOV'25.csv # Sample dataset
├── requirements.txt            # Python dependencies
├── .gitignore                  # Git ignore rules
└── README.md                   # This file
```

## 🎯 Usage Guide

### Data Upload
1. Use the **sidebar file uploader** to upload your CSV timesheet
2. Or use the default sample data to explore features
3. Supported format: CSV with columns for Date, Employee Name, Activity Category, Work Time, Location, Attendance

### Filtering Data
- **Date Range**: Select start and end dates
- **Locations**: Multi-select location filter
- **Trainers**: Multi-select employee filter
- **Configuration**: Set working days and daily working hours for capacity calculations

### Generating Reports
1. Navigate through tabs to explore different analytics
2. Configure PDF export options in sidebar
3. Select desired tables and charts
4. Generate and download PDF report

### Interpreting Metrics

**Utilization Score** = (Billable Hours / Capacity Hours) × 100
- Optimal range: 70-85%
- >90%: Potential burnout risk
- <50%: Underutilization

**Attendance Rate** = (Present Days / Total Days) × 100
- Industry standard: >95%

**Travel Efficiency** = (Onsite Delivery Hours / Total Onsite Hours) × 100
- Good efficiency: >60%
- Needs improvement: <40%

## 🌐 Deployment

### Streamlit Community Cloud

**Live URL**: https://time-sheet-analysis-jqwzv9kmthzhbesg4hq5bu.streamlit.app/

**Deploy Your Own Instance:**
1. Fork this repository
2. Go to [share.streamlit.io](https://share.streamlit.io/)
3. Sign in with GitHub
4. Click "New app"
5. Select your repository, branch (`main`), and main file (`app.py`)
6. Click "Deploy"

### Automatic Updates
- Push changes to GitHub `main` branch
- Streamlit Cloud auto-deploys updates
- No manual intervention required

## 🔒 Security & Privacy

- **No API keys or secrets** in codebase
- **Enhanced .gitignore** for sensitive files
- **Environment variables** excluded from version control
- **Streamlit secrets** properly configured
- **Data privacy**: Upload your own data or use sample dataset

## 🛠️ Configuration

### Sidebar Configuration Options
- **Working Days**: Set expected working days per period (default: 22)
- **Daily Working Hours**: Set standard work hours per day (default: 8)
- **PDF Page Size**: Choose from 9 page size options
- **PDF Orientation**: Portrait or Landscape
- **Table Inclusion**: Select which tables to include in PDF

### Data Requirements
Your CSV should include these columns:
- `Date` - Date of activity
- `Employee Name` - Trainer/employee identifier
- `Activity Category` - Type of activity
- `Work Time (Mins)` - Duration in minutes
- `Location` - Work location
- `Attendance` - Attendance status (P/L/WO/H/A)

## 📊 Sample Data

Included sample dataset: `Time-sheet_2025 - NOV'25.csv`
- **Period**: November 2025
- **Records**: ~1000+ entries
- **Trainers**: Multiple employees
- **Activities**: Training, Travel, Admin, Meetings, etc.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📝 License

This project is licensed under the MIT License.

## 👤 Author

**GitHub**: [@iamazadak](https://github.com/iamazadak)

## 🙏 Acknowledgments

- Built with [Streamlit](https://streamlit.io/)
- Visualizations powered by [Plotly](https://plotly.com/)
- PDF generation using [ReportLab](https://www.reportlab.com/)

---

**Last Updated**: December 2025  
**Version**: 1.0.0
