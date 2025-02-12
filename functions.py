

class Functions:
    @staticmethod
    def calculate_sell_price(pdLSH:float, adL:float) -> float:
        return adL + ((pdLSH - adL) * 0.764)

    @staticmethod
    def calculate_buy_price(pdLSL:float, adH:float) -> float:
        return adH - ((adH - pdLSL) * 0.764)

    @staticmethod
    def calculate_rr(entry_point, stop_loss, profit_target, trade_type="BUY"):
        if trade_type.upper() == "BUY":
            # For BUY: risk is entry - stop_loss, reward is profit_target - entry.
            risk = entry_point - stop_loss
            reward = profit_target - entry_point
        elif trade_type.upper() == "SELL":
            # For SELL: risk is stop_loss - entry, reward is entry - profit_target.
            risk = stop_loss - entry_point
            reward = entry_point - profit_target
        k = reward / risk
        return f"1:{round(k, 2)}"

    @staticmethod
    def calculate_half_fib_sell(pdLSH:float, adL:float) -> float:
        return adL + ((pdLSH - adL) * 0.5)

    @staticmethod
    def calculate_half_fib_buy(pdLSL:float, adH:float) -> float:
        return adH - ((adH - pdLSL) * 0.5)