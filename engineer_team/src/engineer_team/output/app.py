import gradio as gr
from accounts import Account, get_share_price

# Create a simple account for demonstration.
account = Account(account_id="user123", initial_deposit=1000.0)

def create_account(initial_deposit):
    global account
    account = Account(account_id="user123", initial_deposit=initial_deposit)
    return f"Account created with initial deposit of {initial_deposit}."

def deposit_funds(amount):
    try:
        account.deposit(amount)
        return f"Deposit successful. New balance: {account.balance}."
    except ValueError as e:
        return str(e)

def withdraw_funds(amount):
    try:
        account.withdraw(amount)
        return f"Withdrawal successful. New balance: {account.balance}."
    except ValueError as e:
        return str(e)
    
def buy_shares(symbol, quantity):
    try:
        account.buy_shares(symbol, quantity)
        return f"Bought {quantity} shares of {symbol}. New balance: {account.balance}."
    except ValueError as e:
        return str(e)

def sell_shares(symbol, quantity):
    try:
        account.sell_shares(symbol, quantity)
        return f"Sold {quantity} shares of {symbol}. New balance: {account.balance}."
    except ValueError as e:
        return str(e)
    
def portfolio_value():
    return f"Portfolio value: {account.portfolio_value()}."

def profit_or_loss():
    return f"Profit or Loss: {account.profit_or_loss()}."

def get_holdings():
    holdings = account.get_holdings()
    return f"Current holdings: {holdings}."

def get_transactions():
    transactions = account.get_transactions()
    return f"Transactions: {transactions}."

with gr.Blocks() as demo:
    gr.Markdown("## Trading Simulation Platform")

    # Create an account
    with gr.Row():
        initial_deposit_input = gr.Number(label="Initial Deposit")
        create_account_btn = gr.Button("Create Account")
        create_account_output = gr.Textbox()
    create_account_btn.click(create_account, inputs=initial_deposit_input, outputs=create_account_output)
    
    # Deposit funds
    with gr.Row():
        deposit_amount_input = gr.Number(label="Deposit Amount")
        deposit_btn = gr.Button("Deposit")
        deposit_output = gr.Textbox()
    deposit_btn.click(deposit_funds, inputs=deposit_amount_input, outputs=deposit_output)
    
    # Withdraw funds
    with gr.Row():
        withdraw_amount_input = gr.Number(label="Withdraw Amount")
        withdraw_btn = gr.Button("Withdraw")
        withdraw_output = gr.Textbox()
    withdraw_btn.click(withdraw_funds, inputs=withdraw_amount_input, outputs=withdraw_output)

    # Buy shares
    with gr.Row():
        buy_symbol_input = gr.Textbox(label="Buy Symbol")
        buy_quantity_input = gr.Number(label="Buy Quantity")
        buy_shares_btn = gr.Button("Buy Shares")
        buy_shares_output = gr.Textbox()
    buy_shares_btn.click(buy_shares, inputs=[buy_symbol_input, buy_quantity_input], outputs=buy_shares_output)

    # Sell shares
    with gr.Row():
        sell_symbol_input = gr.Textbox(label="Sell Symbol")
        sell_quantity_input = gr.Number(label="Sell Quantity")
        sell_shares_btn = gr.Button("Sell Shares")
        sell_shares_output = gr.Textbox()
    sell_shares_btn.click(sell_shares, inputs=[sell_symbol_input, sell_quantity_input], outputs=sell_shares_output)

    # Portfolio value
    with gr.Row():
        portfolio_val_btn = gr.Button("Get Portfolio Value")
        portfolio_val_output = gr.Textbox()
    portfolio_val_btn.click(portfolio_value, outputs=portfolio_val_output)

    # Profit or loss
    with gr.Row():
        pl_btn = gr.Button("Get Profit or Loss")
        pl_output = gr.Textbox()
    pl_btn.click(profit_or_loss, outputs=pl_output)

    # Get holdings
    with gr.Row():
        holdings_btn = gr.Button("Get Holdings")
        holdings_output = gr.Textbox()
    holdings_btn.click(get_holdings, outputs=holdings_output)

    # Get transactions
    with gr.Row():
        transactions_btn = gr.Button("Get Transactions")
        transactions_output = gr.Textbox()
    transactions_btn.click(get_transactions, outputs=transactions_output)

demo.launch()