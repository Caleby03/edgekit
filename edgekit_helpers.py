
from datetime import datetime
import pandas as pd

def format_hour_label(hour):
    if pd.isna(hour):
        return "Unknown"
    hour = int(hour)
    return datetime.strptime(str(hour), "%H").strftime("%-I %p")
