import unittest
from accounts import Account, get_share_price

class TestAccount(unittest.TestCase):
    def setUp(self):
        self.account = Account('12345', 1000.0)
    
    def test_initialization(self):
        self.assertEqual(self.account.account_id, '12345')
        self.assertEqual(self.account.initial_deposit, 1000.0)
        self.assertEqual(self.account.balance, 1000.0)
        self.assertEqual(self.account.holdings, {})
        self.assertEqual(self.account.transactions, [])

    def test_deposit_positive_amount(self):
        self.account.deposit(500.0)
        self.assertEqual(self.account.balance, 1500.0)
        self.assertEqual(self.account.transactions, [{"type": "deposit", "amount": 500.0}])

    def test_deposit_negative_amount(self):
        with self.assertRaises(ValueError):
            self.account.deposit(-100.0)

    def test_withdraw_positive_amount(self):
        self.account.withdraw(400.0)
        self.assertEqual(self.account.balance, 600.0)
        self.assertEqual(self.account.transactions, [{"type": "withdraw", "amount": 400.0}])

    def test_withdraw_with_insufficient_funds(self):
        with self.assertRaises(ValueError):
            self.account.withdraw(2000.0)

    def test_withdraw_negative_amount(self):
        with self.assertRaises(ValueError):
            self.account.withdraw(-100.0)

    def test_buy_shares_success(self):
        self.account.buy_shares("AAPL", 5)
        self.assertEqual(self.account.balance, 250.0)
        self.assertEqual(self.account.holdings, {"AAPL": 5})
        self.assertEqual(self.account.transactions, [{"type": "buy", "symbol": "AAPL", "quantity": 5, "price": 150.0}])

    def test_buy_shares_insufficient_funds(self):
        with self.assertRaises(ValueError):
            self.account.buy_shares("TSLA", 2)

    def test_buy_shares_negative_quantity(self):
        with self.assertRaises(ValueError):
            self.account.buy_shares("AAPL", -5)

    def test_sell_shares_success(self):
        self.account.buy_shares("AAPL", 5)
        self.account.sell_shares("AAPL", 3)
        self.assertEqual(self.account.balance, 700.0)
        self.assertEqual(self.account.holdings, {"AAPL": 2})
        self.assertEqual(self.account.transactions[-1], {"type": "sell", "symbol": "AAPL", "quantity": 3, "price": 150.0})

    def test_sell_shares_insufficient_shares(self):
        with self.assertRaises(ValueError):
            self.account.sell_shares("AAPL", 1)

    def test_sell_shares_negative_quantity(self):
        with self.assertRaises(ValueError):
            self.account.sell_shares("AAPL", -5)

    def test_portfolio_value(self):
        self.account.buy_shares("AAPL", 5)
        self.account.buy_shares("TSLA", 1)
        self.assertAlmostEqual(self.account.portfolio_value(), 1150.0)

    def test_profit_or_loss(self):
        initial_value = self.account.portfolio_value()
        self.account.buy_shares("AAPL", 5)
        self.assertAlmostEqual(self.account.profit_or_loss(), initial_value - 1000.0)

    def test_get_holdings(self):
        self.account.buy_shares("AAPL", 5)
        self.assertEqual(self.account.get_holdings(), {"AAPL": 5})

    def test_get_transactions(self):
        self.account.deposit(200.0)
        self.account.withdraw(100.0)
        self.assertEqual(len(self.account.get_transactions()), 2)

class TestGetSharePrice(unittest.TestCase):
    def test_get_share_price_known_symbol(self):
        self.assertEqual(get_share_price("AAPL"), 150.0)

    def test_get_share_price_unknown_symbol(self):
        self.assertEqual(get_share_price("UNKNOWN"), 0.0)

if __name__ == '__main__':
    unittest.main()