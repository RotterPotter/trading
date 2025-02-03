import pandas as pd

if __name__ == "__main__":
    file_path = "data.csv"

    # Read CSV file into a pandas DataFrame
    data = pd.read_csv(file_path)

    # Convert "Date" column to datetime format
    data["Date"] = pd.to_datetime(data["Date"], format="%Y.%m.%d")

    # Define start and end dates for filtering
    date_start_str = "2004-06-23"
    date_end_str = "2004-07-23"
    date_start_datetime = pd.to_datetime(date_start_str)
    date_end_datetime = pd.to_datetime(date_end_str)

    # Filter data based on date range
    filtered_data = data[(data["Date"] >= date_start_datetime) & (data["Date"] <= date_end_datetime)]
    print(filtered_data)