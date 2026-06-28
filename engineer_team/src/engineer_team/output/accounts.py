class Account:
    def __init__(self, account_id: str, initial_deposit: float) -> None:
        self.account_id = account_id
        self.initial_deposit = initial_deposit
        self.balance = initial_deposit
        self.holdings = {}
        self.transactions = []

    def deposit(self, amount: float) -> None:
        if amount <= 0:
            raise ValueError("Deposit amount must be positive.")
        self.balance += amount
        self.transactions.append({"type": "deposit", "amount": amount})

    def withdraw(self, amount: float) -> None:
        if amount <= 0:
            raise ValueError("Withdrawal amount must be positive.")
        if amount > self.balance:
            raise ValueError("Insufficient funds for withdrawal.")
        self.balance -= amount
        self.transactions.append({"type": "withdraw", "amount": amount})

    def buy_shares(self, symbol: str, quantity: int) -> None:
        if quantity <= 0:
            raise ValueError("Quantity must be positive.")
        price_per_share = get_share_price(symbol)
        total_cost = price_per_share * quantity
        if total_cost > self.balance:
            raise ValueError("Insufficient funds to buy shares.")
        self.balance -= total_cost
        if symbol in self.holdings:
            self.holdings[symbol] += quantity
        else:
            self.holdings[symbol] = quantity
        self.transactions.append({"type": "buy", "symbol": symbol, "quantity": quantity, "price": price_per_share})

    def sell_shares(self, symbol: str, quantity: int) -> None:
        if quantity <= 0:
            raise ValueError("Quantity must be positive.")
        if symbol not in self.holdings or self.holdings[symbol] < quantity:
            raise ValueError("Insufficient shares to sell.")
        price_per_share = get_share_price(symbol)
        total_revenue = price_per_share * quantity
        self.holdings[symbol] -= quantity
        if self.holdings[symbol] == 0:
            del self.holdings[symbol]
        self.balance += total_revenue
        self.transactions.append({"type": "sell", "symbol": symbol, "quantity": quantity, "price": price_per_share})

    def portfolio_value(self) -> float:
        total_value = self.balance
        for symbol, quantity in self.holdings.items():
            total_value += get_share_price(symbol) * quantity
        return total_value

    def profit_or_loss(self) -> float:
        return self.portfolio_value() - self.initial_deposit

    def get_holdings(self) -> dict:
        return dict(self.holdings)

    def get_transactions(self) -> list:
        return list(self.transactions)

def get_share_price(symbol: str) -> float:
    prices = {
        "AAPL": 150.0,
        "TSLA": 700.0,
        "GOOGL": 2800.0
    }
    return prices.get(symbol, 0.0)