import pandas as pd
from typing import Dict
from datetime import datetime

LONDON_SESSION_START = "9:00"
LONDON_SESSION_END = "15:00"

def take_parameters(
    current_datetime: datetime,
    file_path: str,
) -> Dict[str, float]:
    """
      Calculate variables: 
        - pdLSH (previous day London session high)
        - pdLSL (precious day London sesssion low)
        - adH (actual day high)
        - adL (actual day low)
    """

    df = pd.read_csv(file_path)

    df["DateTime"] = pd.to_datetime(df["Date"] + " " + df["Time"])
    df.drop(columns=["Date", "Time"], inplace=True)  # Drop the old columns 

    previous_day = current_datetime - pd.Timedelta(days=1)
    previous_day_start = pd.to_datetime(f"{previous_day.date()} {LONDON_SESSION_START}")
    previous_day_end = pd.to_datetime(f"{previous_day.date()} {LONDON_SESSION_END}")
    previous_day_data = df[(df["DateTime"] >= previous_day_start) & (df["DateTime"] <= previous_day_end)]

    pdLSH = previous_day_data["High"].max() if not previous_day_data.empty else None
    pdLSL = previous_day_data["Low"].min() if not previous_day_data.empty else None

    filtered_data = df[(df["DateTime"] >= (current_datetime - pd.Timedelta(minutes=10))) & (df["DateTime"] <= current_datetime)]
    adH = filtered_data["High"].max() if not filtered_data.empty else None
    adL = filtered_data["Low"].min() if not filtered_data.empty else None

    return {
        "pdLSH": pdLSH,
        "pdLSL": pdLSL,
        "adH": adH,
        "adL": adL
    }

def calculate_sell_price(pdLSH:float, adL:float) -> float:
    return adL + ((pdLSH - adL) * 0.764)

def calculate_half_fib_sell(pdLSH:float, adL:float) -> float:
    return (pdLSH - adL) * 0.5

def calculate_buy_price(pdLSL:float, adH:float) -> float:
    return adH + ((adH - pdLSL) * 0.764)

def calculate_half_fib_buy(pdLSL:float, adH:float) -> float:
    return (adH - pdLSL) * 0.5
