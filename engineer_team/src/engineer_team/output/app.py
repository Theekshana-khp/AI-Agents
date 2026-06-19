import gradio as gr
from accounts import Account, get_share_price

# Initialize a global account object
account = Account(account_id="user_001", initial_deposit=1000.0)

def create_account(initial_deposit):
    global account
    account = Account(account_id="user_001", initial_deposit=initial_deposit)
    return f"Account created with initial deposit of {initial_deposit}"

def deposit_funds(amount):
    try:
        account.deposit_funds(amount)
        return f"Deposited {amount}. New balance: {account.balance}"
    except ValueError as e:
        return str(e)

def withdraw_funds(amount):
    try:
        account.withdraw_funds(amount)
        return f"Withdrew {amount}. New balance: {account.balance}"
    except ValueError as e:
        return str(e)

def buy_shares(symbol, quantity):
    try:
        account.buy_shares(symbol, quantity)
        return f"Bought {quantity} shares of {symbol}. New balance: {account.balance}"
    except ValueError as e:
        return str(e)

def sell_shares(symbol, quantity):
    try:
        account.sell_shares(symbol, quantity)
        return f"Sold {quantity} shares of {symbol}. New balance: {account.balance}"
    except ValueError as e:
        return str(e)

def view_portfolio_value():
    return f"Total Portfolio Value: {account.calculate_portfolio_value()}"

def view_profit_or_loss():
    return f"Profit/Loss: {account.calculate_profit_or_loss()}"

def view_holdings():
    holdings = account.get_holdings()
    return f"Holdings: {holdings}"

def view_transactions():
    transactions = account.get_transaction_history()
    return "\n".join([f"Type: {t[0]}, Symbol: {t[1]}, Quantity: {t[2]}, Price: {t[3]}, Date: {t[4]}" for t in transactions])

with gr.Blocks() as demo:
    gr.Markdown("## Trading Simulation Platform")
    
    with gr.Tab("Account Management"):
        initial_deposit = gr.Number(label="Initial Deposit")
        deposit_button = gr.Button("Create Account")
        deposit_button.click(create_account, [initial_deposit], gr.Textbox(label="Output"))
        
        deposit_amount = gr.Number(label="Deposit Amount")
        deposit_button = gr.Button("Deposit Funds")
        deposit_button.click(deposit_funds, [deposit_amount], gr.Textbox(label="Output"))

        withdraw_amount = gr.Number(label="Withdraw Amount")
        withdraw_button = gr.Button("Withdraw Funds")
        withdraw_button.click(withdraw_funds, [withdraw_amount], gr.Textbox(label="Output"))

    with gr.Tab("Trade Shares"):
        stock_symbol = gr.Dropdown(choices=["AAPL", "TSLA", "GOOGL"], label="Stock Symbol")
        quantity = gr.Number(label="Quantity")

        buy_button = gr.Button("Buy Shares")
        buy_button.click(buy_shares, [stock_symbol, quantity], gr.Textbox(label="Output"))

        sell_button = gr.Button("Sell Shares")
        sell_button.click(sell_shares, [stock_symbol, quantity], gr.Textbox(label="Output"))

    with gr.Tab("Reports"):
        view_portfolio_button = gr.Button("View Portfolio Value")
        view_portfolio_button.click(view_portfolio_value, [], gr.Textbox(label="Portfolio Value"))

        view_profit_button = gr.Button("View Profit/Loss")
        view_profit_button.click(view_profit_or_loss, [], gr.Textbox(label="Profit/Loss"))

        view_holdings_button = gr.Button("View Holdings")
        view_holdings_button.click(view_holdings, [], gr.Textbox(label="Holdings"))

        view_transactions_button = gr.Button("View Transactions")
        view_transactions_button.click(view_transactions, [], gr.Textbox(label="Transactions"))

demo.launch()