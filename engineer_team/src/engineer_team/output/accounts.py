
from datetime import datetime

def get_share_price(symbol: str) -> float:
    prices = {
        "AAPL": 150.0,
        "TSLA": 600.0,
        "GOOGL": 2800.0
    }
    return prices.get(symbol, 0.0)

class Account:
    def __init__(self, account_id: str, initial_deposit: float) -> None:
        self.account_id = account_id
        self.balance = initial_deposit
        self.initial_deposit = initial_deposit
        self.holdings = {}
        self.transaction_history = []
    
    def deposit_funds(self, amount: float) -> None:
        if amount <= 0:
            raise ValueError("Deposit amount must be positive.")
        self.balance += amount
        self.transaction_history.append(("Deposit", None, None, amount, datetime.now()))
    
    def withdraw_funds(self, amount: float) -> None:
        if amount <= 0:
            raise ValueError("Withdrawal amount must be positive.")
        if amount > self.balance:
            raise ValueError("Insufficient funds.")
        self.balance -= amount
        self.transaction_history.append(("Withdraw", None, None, amount, datetime.now()))
    
    def buy_shares(self, symbol: str, quantity: int) -> None:
        if quantity <= 0:
            raise ValueError("Quantity must be positive.")
        share_price = get_share_price(symbol)
        total_cost = share_price * quantity
        if total_cost > self.balance:
            raise ValueError("Insufficient funds to buy shares.")
        self.balance -= total_cost
        if symbol in self.holdings:
            self.holdings[symbol] += quantity
        else:
            self.holdings[symbol] = quantity
        self.transaction_history.append(("Buy", symbol, quantity, share_price, datetime.now()))
    
    def sell_shares(self, symbol: str, quantity: int) -> None:
        if quantity <= 0:
            raise ValueError("Quantity must be positive.")
        if symbol not in self.holdings or self.holdings[symbol] < quantity:
            raise ValueError("Insufficient shares to sell.")
        share_price = get_share_price(symbol)
        total_value = share_price * quantity
        self.balance += total_value
        self.holdings[symbol] -= quantity
        if self.holdings[symbol] == 0:
            del self.holdings[symbol]
        self.transaction_history.append(("Sell", symbol, quantity, share_price, datetime.now()))
    
    def calculate_portfolio_value(self) -> float:
        portfolio_value = self.balance
        for symbol, quantity in self.holdings.items():
            share_price = get_share_price(symbol)
            portfolio_value += share_price * quantity
        return portfolio_value
    
    def calculate_profit_or_loss(self) -> float:
        current_value = self.calculate_portfolio_value()
        return current_value - self.initial_deposit
    
    def get_holdings(self) -> dict:
        return self.holdings.copy()
    
    def get_transaction_history(self) -> list:
        return self.transaction_history.copy()
