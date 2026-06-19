import unittest
from accounts import Account, get_share_price
from datetime import datetime

class TestGetSharePrice(unittest.TestCase):

    def test_get_share_price_valid_symbol(self):
        self.assertEqual(get_share_price("AAPL"), 150.0)
        self.assertEqual(get_share_price("TSLA"), 600.0)
        self.assertEqual(get_share_price("GOOGL"), 2800.0)

    def test_get_share_price_invalid_symbol(self):
        self.assertEqual(get_share_price("INVALID"), 0.0)

class TestAccount(unittest.TestCase):

    def setUp(self):
        self.account = Account("acc123", 1000.0)

    def test_initialization(self):
        self.assertEqual(self.account.account_id, "acc123")
        self.assertEqual(self.account.balance, 1000.0)
        self.assertEqual(self.account.initial_deposit, 1000.0)
        self.assertEqual(self.account.holdings, {})
        self.assertEqual(self.account.transaction_history, [])

    def test_deposit_funds(self):
        self.account.deposit_funds(500.0)
        self.assertEqual(self.account.balance, 1500.0)
        self.assertEqual(len(self.account.transaction_history), 1)
        self.assertEqual(self.account.transaction_history[0][0], "Deposit")

    def test_deposit_funds_negative(self):
        with self.assertRaises(ValueError):
            self.account.deposit_funds(-100.0)

    def test_withdraw_funds(self):
        self.account.withdraw_funds(500.0)
        self.assertEqual(self.account.balance, 500.0)
        self.assertEqual(len(self.account.transaction_history), 1)
        self.assertEqual(self.account.transaction_history[0][0], "Withdraw")

    def test_withdraw_funds_insufficient(self):
        with self.assertRaises(ValueError):
            self.account.withdraw_funds(1500.0)

    def test_withdraw_funds_negative(self):
        with self.assertRaises(ValueError):
            self.account.withdraw_funds(-100.0)

    def test_buy_shares(self):
        self.account.buy_shares("AAPL", 2)
        self.assertEqual(self.account.balance, 700.0)  # 1000 - (150 * 2)
        self.assertEqual(self.account.holdings["AAPL"], 2)
        self.assertEqual(len(self.account.transaction_history), 1)
        self.assertEqual(self.account.transaction_history[0][0], "Buy")

    def test_buy_shares_insufficient_funds(self):
        with self.assertRaises(ValueError):
            self.account.buy_shares("TSLA", 2)

    def test_buy_shares_negative_quantity(self):
        with self.assertRaises(ValueError):
            self.account.buy_shares("AAPL", -1)

    def test_sell_shares(self):
        self.account.buy_shares("AAPL", 2)
        self.account.sell_shares("AAPL", 1)
        self.assertEqual(self.account.balance, 850.0)  # 700 + (150 * 1)
        self.assertEqual(self.account.holdings["AAPL"], 1)
        self.assertEqual(len(self.account.transaction_history), 2)
        self.assertEqual(self.account.transaction_history[1][0], "Sell")

    def test_sell_shares_insufficient_shares(self):
        with self.assertRaises(ValueError):
            self.account.sell_shares("AAPL", 1)

    def test_sell_shares_negative_quantity(self):
        with self.assertRaises(ValueError):
            self.account.sell_shares("AAPL", -1)

    def test_calculate_portfolio_value(self):
        self.account.buy_shares("AAPL", 2)
        portfolio_value = self.account.calculate_portfolio_value()
        self.assertEqual(portfolio_value, 1000.0)

    def test_calculate_profit_or_loss(self):
        self.account.buy_shares("AAPL", 2)
        profit_or_loss = self.account.calculate_profit_or_loss()
        self.assertEqual(profit_or_loss, 0.0)

    def test_get_holdings(self):
        self.account.buy_shares("AAPL", 2)
        holdings = self.account.get_holdings()
        self.assertEqual(holdings, {"AAPL": 2})

    def test_get_transaction_history(self):
        self.account.deposit_funds(500.0)
        history = self.account.get_transaction_history()
        self.assertEqual(len(history), 1)
        self.assertEqual(history[0][0], "Deposit")

if __name__ == "__main__":
    unittest.main()