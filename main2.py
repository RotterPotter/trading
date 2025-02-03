import pandas as pd
from datetime import datetime
from typing import Optional
import functions

"""
  Algorithm:
  1. Take 1 date day data from data.csv
  2. Execute get_parameters function to calculate day params: 
    - pdLSH Previous Day London Session High
    - pdLSL Previous Day London Session Low
    - adH Actual Day High
    - adL Actual Day Low
  3. Start iteration between day candles.
  4. Take 15 min candle parameters:
    - cH Candle High
    - cL Candle Low

"""
def main():
  weekdays = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]

  # Define start/end trading time
  START_TIME = datetime.strptime("6:00", "%H:%M").time()
  NO_MORE_TRADES_TIME = datetime.strptime("14:30", "%H:%M").time()
  END_TIME = datetime.strptime("15:25", "%H:%M").time()
  
  # Define start/end London session time
  LONDON_SESSION_START_TIME = datetime.strptime("9:00", "%H:%M").time()
  LONDON_SESSION_END_TIME = datetime.strptime("15:00", "%H:%M").time()

  # Load data.csv file to dataframe
  df = pd.read_csv("data.csv")

  # Convert the date column to datetime format
  df['Date'] = pd.to_datetime(df['Date'])

  # define raport dataframe structure
  raport_columns = ["Name", "Date", "Weekday", "Time", "Type", "Asset", "R:R", "Result", "P/L"]
  raport_df = pd.DataFrame(columns=raport_columns)

  # Define start and end dates (as strings)
  start_date = "2006-06-15"
  end_date = "2006-06-22"

  # Convert start date and end date to datetime objects
  start_datetime = pd.to_datetime(start_date)
  end_datetime = pd.to_datetime(end_date)

  hero_date = start_datetime

  # Loop in dates
  while hero_date <= end_datetime:
    # define variable for active order type
    active_order = None

    # take date data slice from main dataframe
    hero_date_df = df[df['Date'] == hero_date]
    
    # take previous day London session df
    pd_datetime = hero_date - pd.Timedelta(days=1)
    previous_day_df = df[df['Date'] == (pd_datetime)]
    previous_day_df["Time"] = previous_day_df["Time"].apply(lambda x: datetime.strptime(x, "%H:%M").time())
    pdls_df = previous_day_df[(previous_day_df["Time"] >= LONDON_SESSION_START_TIME) & (previous_day_df["Time"] <= LONDON_SESSION_END_TIME)]
    
    # if no previous day london session data, continue
    if pdls_df.empty:
      continue

    # set day variables
    pdLSH: float = pdls_df["Close"].max() # previousDayLondonSessionHigh
    pdLSL: float = pdls_df["Close"].min()# previousDayLondonSessionLow

    # take actual day df before 6 AM (to extract adH and adL)
    hero_date_df_copy = hero_date_df.copy()
    hero_date_df_copy["Time"] = hero_date_df_copy["Time"].apply(lambda x: datetime.strptime(x, "%H:%M").time())
    hero_date_df_before_start = hero_date_df_copy[hero_date_df_copy["Time"] <= START_TIME]

    # actual day params 
    adH: float = hero_date_df_before_start["Close"].max() #actualDayHigh 
    adL: float = hero_date_df_before_start["Close"].min() #actualDayLow 
    sell_price: Optional[float] = None
    half_fib_sell: Optional[float] = None
    buy_price: Optional[float] = None
    half_fib_buy: Optional[float] = None
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None
    risk: Optional[float] = None
    reward: Optional[float] = None
    reward_to_risk: Optional[str] = None

    # Iterate in candles (dataframe rows)
    for candle_data in hero_date_df.itertuples(index=False):
      candle_time = datetime.strptime(candle_data.Time, "%H:%M").time()
      if candle_time < START_TIME:
        # no trades before start time
        continue
      elif NO_MORE_TRADES_TIME <= candle_time < END_TIME:
        # no more new trades between 14:30 and 15:25
        continue
      elif candle_time >= END_TIME:
        # TODO
        # if there is opened trade after 15:25, close it
        continue
      
      # Update day params if needed
      if candle_data.Close > adH:
        adH = candle_data.Close
      elif candle_data.Close < adL:
        adL = candle_data.Close

      if (pdLSH > adL) and (pdLSH > adH):
        sell_price = functions.calculate_sell_price(pdLSH, adL)
        half_fib_sell = functions.calculate_half_fib_sell(pdLSH, adL)
      elif (pdLSL < adH) and (pdLSL < adL):
        buy_price = functions.calculate_buy_price(pdLSL, adH)
        half_fib_buy = functions.calculate_half_fib_buy(pdLSL, adH)
      
      if active_order is None:
        # if price reached sell price
        if (sell_price is not None) and (candle_data.Close >= sell_price):
          # execute sell order
          active_order = "SELL"
          stop_loss = pdLSH 
          take_profit = adL 
          risk = stop_loss - sell_price
          reward = sell_price - take_profit
          reward_to_risk = f"1:{round(reward/risk, 2)}"
          new_data = pd.DataFrame([["OPENING", hero_date.date(), weekdays[hero_date.weekday()], candle_time, "SELL", "XAUUSD", reward_to_risk, None, None]],
                                            columns=raport_columns)
          print(new_data)
          raport_df = pd.concat([df, new_data])
          
        elif (buy_price is not None) and (candle_data.Close <= buy_price):
          stop_loss = pdLSL
          take_profit = adH
          risk = buy_price - stop_loss
          reward = take_profit - buy_price
          reward_to_risk = f"1:{round(reward/risk, 2)}"
          new_data = pd.DataFrame([["OPENING", hero_date.date(), weekdays[hero_date.weekday()], candle_time, "BUY", "XAUUSD", reward_to_risk, None, None]],
                                            columns=raport_columns)
          print(new_data)
          raport_df = pd.concat([df, new_data])

      elif active_order == "SELL":
        # if stop loss hit
        if candle_data.Close >= stop_loss:
          new_data = pd.DataFrame([["CLOSING", hero_date.date(), weekdays[hero_date.weekday()], candle_time, "SELL", "XAUUSD", reward_to_risk, "LOSS", "-1"]],
                                            columns=raport_columns)
          print(new_data)
          raport_df = pd.concat([df, new_data])
          active_order = None
        # if take profit hit
        elif candle_data.Close <= take_profit:
          pl = "+" + reward_to_risk.split(":")[1]
          new_data = pd.DataFrame([["CLOSING", hero_date.date(), weekdays[hero_date.weekday()], candle_time, "SELL", "XAUUSD", reward_to_risk, "WIN", pl]],
                                            columns=raport_columns)
          print(new_data)
          raport_df = pd.concat([df, new_data])
          active_order = None

      elif active_order == "BUY":
        # if stop loss hit
        if candle_data.Close <= stop_loss:
          new_data = pd.DataFrame([["CLOSING", hero_date.date(), weekdays[hero_date.weekday()], candle_time, "BUY", "XAUUSD", reward_to_risk, "LOSS", "-1"]],
                                            columns=raport_columns)
          print(new_data)
          raport_df = pd.concat([df, new_data])
          active_order = None
        # if take profit hit
        elif candle_data.Close >= take_profit:
          pl = "+" + reward_to_risk.split(":")[1]
          new_data = pd.DataFrame([["CLOSING", hero_date.date(), weekdays[hero_date.weekday()], candle_time, "BUY", "XAUUSD", reward_to_risk, "WIN", pl]],
                                            columns=raport_columns)
          print(new_data)
          raport_df = pd.concat([df, new_data])
          active_order = None

    # Adjust one day to hero_date at the end
    hero_date += pd.Timedelta(days=1)

  return raport_df
    


  

if __name__ == "__main__":
  raport = main()
  print(raport)