# Time-Sheet Analysis Dashboard

A comprehensive Streamlit-based dashboard for analyzing employee time-sheet data with interactive visualizations and insights.

## Features

- **Executive Dashboard**: Overview of key metrics and KPIs
- **Trainer 360 Profile**: Individual trainer performance analysis
- **Activity Analysis**: Breakdown of activities and time allocation
- **Productivity Metrics**: Track productivity trends and patterns
- **Location Analysis**: Geographic distribution of work
- **Travel Analysis**: Travel time and patterns
- **Attendance Tracking**: Monitor attendance and working hours
- **Training Insights**: Training session analytics
- **Trend Analysis**: Historical trends and patterns
- **Raw Data Explorer**: Filter and export raw data

## Installation

1. Clone the repository:
```bash
git clone <your-repo-url>
cd Time-Sheet\ Analysis
```

2. Create and activate a virtual environment:
```bash
python -m venv .venv
.\.venv\Scripts\Activate.ps1  # Windows PowerShell
```

3. Install dependencies:
```bash
pip install streamlit plotly pandas numpy
```

## Usage

Run the Streamlit app:
```bash
streamlit run app.py
```

The app will open in your default browser at `http://localhost:8501`

## Project Structure

```
Time-Sheet Analysis/
├── app.py                      # Main Streamlit application
├── data_processor.py           # Data processing utilities
├── color_gen.py               # Color palette generator
├── analysis_activities.py     # Activity analysis module
├── analysis_attendance.py     # Attendance analysis module
├── analysis_location.py       # Location analysis module
├── analysis_productivity.py   # Productivity analysis module
├── analysis_training.py       # Training analysis module
├── analysis_travel.py         # Travel analysis module
├── analysis_trends.py         # Trend analysis module
├── Time-sheet_2025 - NOV'25.csv  # Sample data file
└── README.md                  # This file
```

## Requirements

- Python 3.8+
- Streamlit
- Plotly
- Pandas
- NumPy

## License

This project is licensed under the MIT License.
