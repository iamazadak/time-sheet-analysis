import pandas as pd
import numpy as np
import re
from datetime import datetime

def load_and_clean_data(file_path):
    """
    Loads the timesheet CSV and flattens it into a long-format DataFrame.
    """
    try:
        # Load Raw Data: Rows 0 is metadata/empty, Row 1 is Dates, Row 2 is Headers
        # we will load with header=None to manually handle the structure
        df_raw = pd.read_csv(file_path, header=None)
    except Exception as e:
        return pd.DataFrame(), f"Error loading CSV: {e}"

    # Row 1 contains Dates (Index 1)
    # Row 2 contains Column Headers (Index 2)
    # Row 3 onwards is data (Index 3)
    
    date_row_idx = 1
    header_row_idx = 2
    data_start_idx = 3

    # Extract Employee Info and Dates
    # Cols 0-6 are fixed info: Sl. No., Employee Name, Location, P, L, A, WO/H
    # This logic assumes the structure is consistent
    
    # 1. Forward Fill Employee Names and Locations on the raw dataframe first?
    # Actually, it's safer to extract the data rows and then ffill.
    
    try:
        data = df_raw.iloc[data_start_idx:].copy()
        data.reset_index(drop=True, inplace=True)
        
        # Column mapping based on inspection
        # C1: Employee Name, C2: Location
        # We need to forward fill these for purely empty rows that contain task data
        
        # Ensure 'Employee Name' (Col 1) is treated as NaN if empty string/whitespace
        data[1] = data[1].replace(r'^\s*$', np.nan, regex=True)
        data[2] = data[2].replace(r'^\s*$', np.nan, regex=True)
        
        data[1] = data[1].ffill()
        data[2] = data[2].ffill()
        
        # Remove rows where Employee Name is still NaN (header junk or footer junk)
        data = data.dropna(subset=[1])
        
        # Now iterate through date columns
        dates_row = df_raw.iloc[date_row_idx]
        headers_row = df_raw.iloc[header_row_idx]
        
        processed_rows = []
        
        # Identifying columns that start a Day block
        # We look for valid dates in dates_row
        
        current_date_str = None
        
        # Iterate over columns starting from index 7
        total_cols = df_raw.shape[1]
        
        # We assume a stride or just look for date headers
        # A safer approach: Iterate columns, if dates_row[col] is a Date, set current_date.
        # Then map the subsequent columns to fields until next date or end.
        
        # Define expected sub-headers relative to a block
        # Based on file: Attendance, Activity Category, Task Priority, Start, End, Work Time, Description
        
        # Let's map column indices to their role for the *current* date context
        # We will build a map: col_idx -> (Date, FieldName)
        
        col_map = {}
        
        for c in range(7, total_cols):
            val = str(dates_row[c]).strip()
            if val and val.lower() != 'nan':
                 current_date_str = val
            
            header_val = str(headers_row[c]).strip()
            
            # Map headers to standardized keys
            if 'Attendance' in header_val:
                field = 'Attendance_Status'
            elif 'Activity Category' in header_val:
                field = 'Activity Category'
            elif 'Task Priority' in header_val:
                field = 'Task Priority'
            elif 'Start' in header_val:
                field = 'Start Time'
            elif 'End' in header_val:
                field = 'End Time'
            elif 'Work Time' in header_val or 'Mins' in header_val:
                field = 'Work Time (Mins)'
            elif 'Description' in header_val:
                field = 'Description'
            else:
                field = None
            
            if current_date_str and field:
                col_map[c] = (current_date_str, field)
        
        # Now iterate through data rows and extract objects
        # To optimize, we can pivot or stack, but row-by-row simple iteration is robust for jagged data
        
        for idx, row in data.iterrows():
            emp_name = row[1]
            location = row[2]
            
            # We need to bundle cells into task objects. 
            # Since each day has multiple columns, we group by Date.
            
            # temporary storage for the row's tasks
            # tasks_by_date = { 'Sat, Nov 01, 25': { 'Start Time': ..., 'End Time': ... } } 
            
            row_tasks = {}
            
            for col_idx, (date_str, field) in col_map.items():
                cell_val = row[col_idx]
                
                if date_str not in row_tasks:
                    row_tasks[date_str] = {}
                
                row_tasks[date_str][field] = cell_val
                
            # Now flatten row_tasks into the list
            for date_str, task_data in row_tasks.items():
                # Filter out empty tasks
                # A task is valid if it has at least an Activity Category OR Description
                # AND it's not fully NaN
                
                activity = str(task_data.get('Activity Category', '')).strip()
                desc = str(task_data.get('Description', '')).strip()
                
                if (activity == '' or activity.lower() == 'nan') and (desc == '' or desc.lower() == 'nan'):
                    continue
                
                entry = {
                    'Employee Name': emp_name,
                    'Location': location,
                    'Date': date_str,
                    'Attendance': task_data.get('Attendance_Status', np.nan),
                    'Activity Category': task_data.get('Activity Category', np.nan),
                    'Task Priority': task_data.get('Task Priority', np.nan),
                    'Start Time': task_data.get('Start Time', np.nan),
                    'End Time': task_data.get('End Time', np.nan),
                    'Work Time (Mins)': task_data.get('Work Time (Mins)', 0),
                    'Description': task_data.get('Description', ''),
                }
                processed_rows.append(entry)

        df = pd.DataFrame(processed_rows)
        
        # Post-Processing
        if df.empty:
            return df, "No data found."

        # Parse Date
        # Data format example: "Sat, Nov 01, 25"
        # We need to parse this to datetime
        def parse_custom_date(d_str):
            try:
                # "Sat, Nov 01, 25" -> %a, %b %d, %y
                clean_d = re.sub(r'(\d+)(st|nd|rd|th)', r'\1', str(d_str)) # Remove ordinal if any
                return datetime.strptime(clean_d, "%a, %b %d, %y")
            except:
                return pd.NaT

        df['Date_Obj'] = df['Date'].apply(parse_custom_date)
        df['Month'] = df['Date_Obj'].dt.strftime('%B')
        df['Week'] = df['Date_Obj'].dt.isocalendar().week
        df['DayOfWeek'] = df['Date_Obj'].dt.day_name()

        # Clean "Work Time (Mins)"
        def clean_minutes(x):
            try:
                if pd.isna(x) or str(x).strip() == '':
                    return 0
                return float(str(x).replace(',', ''))
            except:
                return 0
        
        df['Work Time (Mins)'] = df['Work Time (Mins)'].apply(clean_minutes)

        # Derived Column: Is_Billable
        # Billable: "Training", "Assessment", "Content Development" (As per usage?)
        # User defined: "Training + Assessment = Billable; Meetings, Travel, Admin = Non-billable"
        # We need to check category names.
        
        billable_keywords = ['Training', 'Assessment', 'Content', 'Development']
        
        def check_billable(cat):
            cat_str = str(cat).lower()
            if any(k.lower() in cat_str for k in billable_keywords):
                return True
            return False
            
        df['Is_Billable'] = df['Activity Category'].apply(check_billable)
        
        return df, None
        
    except Exception as e:
        import traceback
        return pd.DataFrame(), f"Error processing data: {str(e)}\n{traceback.format_exc()}"

if __name__ == "__main__":
    # Test run
    df, err = load_and_clean_data("Time-sheet_2025 - NOV'25.csv")
    if err:
        print(err)
    else:
        print(df.head())
        print(df.info())
