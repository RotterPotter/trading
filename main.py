import pandas as pd

LONDON_SESSION_START = "9:00"
LONDON_SESSION_END = "15:00"

def take_parameters(
    current_date_and_time: str,
    file_path: str,
):
    current_datetime = pd.to_datetime(current_date_and_time)

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
  
if __name__ == "__main__":
    result = take_parameters(current_date_and_time="2004.06.16 06:00:00", file_path='data.csv')
    print(result)
