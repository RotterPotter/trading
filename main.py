import functions
from datetime import datetime, timedelta
import pandas as pd

if __name__ == "__main__":
    df = pd.read_csv("data.csv")  

    for date in pd.unique(df["Date"]):
        # 6am start
        start_datetime = datetime.strptime(f"{date} 06:00:00", "%Y.%m.%d %H:%M:%S")
        # 14:30 end
        end_datetime = datetime.strptime(f"{date} 14:30:00", "%Y.%m.%d %H:%M:%S")
        # loop until 14:30
        day_params = functions.take_parameters(start_datetime, "data.csv")
        missed_data = False
        # if missed data, skip day
        for day_param in day_params.values():
            if day_param is None:
                missed_data = True
                break
        if missed_data == True:
            continue
        pdLSH = day_params["pdLSH"]
        pdLSL = day_params["pdLSL"]
        adH = day_params["adH"]
        adL = day_params["adL"]

        sell_price = None
        buy_price = None
        half_fib_sell = None
        half_fib_buy = None

        SL = None
        TP = None
        risk = None
        reward = None
        RR = None

        active_order_type = None

        while start_datetime <= end_datetime:
            
            # take candle params
            candle_params = functions.take_parameters(start_datetime, "data.csv")
            
            # if missed data, skip candle
            missed_data = False
            for candle_param in candle_params.values():
                if candle_param is None:
                    missed_data = True
                    break
            if missed_data == True:
                start_datetime += timedelta(minutes=15)
                continue
            
            # update day params if needed
            if candle_params["adH"] > day_params["adH"]:
                day_params["adH"] = candle_params["adH"]
            if candle_params["adL"] < day_params["adL"]:
                day_params["adL"] = candle_params["adL"]
            

            if (pdLSH > adL) and (pdLSH > adH):
                sell_price = functions.calculate_sell_price(pdLSH, adL)
                half_fib_sell = functions.calculate_half_fib_sell(pdLSH, adL)


            if (pdLSL < adH) and (pdLSL < adL):
                buy_price = functions.calculate_buy_price(pdLSL, adH)
                half_fib_buy = functions.calculate_half_fib_buy(pdLSL, adH)

            candle = df[
                (df["Date"] == start_datetime.strftime("%Y.%m.%d")) & 
                (df["Time"].str.startswith(start_datetime.strftime("%H:%M")))
            ]
            
            print(candle)
            print(sell_price)
            print(buy_price)
            print("-"*10)

            if active_order_type == "SELL":
                # if stop loss hit
                if candle["High"].item() >= SL:
                    pass
                # if take profit hit
                elif candle["Low"].item() <= TP:
                    pass
            elif active_order_type == "BUY":
                # if stop loss hit
                if candle["Low"].item() <= SL:
                    pass
                elif candle["High"].item() >= TP:
                    pass
            
            elif active_order_type is None:
                if sell_price is not None and candle["High"].item() >= sell_price:
                    active_order_type = "SELL"
                    SL = pdLSH
                    TP = adL
                    risk = SL - sell_price
                    reward = sell_price - TP
                    if risk > 0:
                        RR = f"1 : {round(reward / risk, 2)}"
                    else:
                        RR = "Undefined (risk <= 0)"

                elif buy_price is not None and candle["Low"].item() <= buy_price:
                    active_order_type = "BUY"
                    SL = pdLSL
                    TP = adH
                    risk = buy_price - SL
                    reward = TP - buy_price
                    if risk > 0:
                        RR = f"1 : {round(reward / risk, 2)}"  
                    else:
                        RR = "Undefined (risk <= 0)"

                start_datetime += timedelta(minutes=15)
                
            

            
            
    

    
    
