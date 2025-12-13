from flask import Flask, request, redirect, render_template, session
from cs50 import SQL
from helper_functions import usd
from api_handlers import get_balance_for_account

# Configure application
app = Flask(__name__)

# Jinja filters
app.jinja_env.filters["usd"] = usd

# Configure cs50 library to use SQlite database
db = SQL("sqlite:///tracker.db")

# Networth calculation
def calculate_networth():
    # Get all accounts
    accounts = db.execute("SELECT * FROM accounts")

    for acct in accounts:
        if acct["source_type"] == "api":
            latest = get_balance_for_account(acct)

            if latest is not None:
                db.execute("UPDATE accounts SET balance = ? WHERE id = ?", latest, acct["id"])

    # After updating balances, recompute totals
    assets = db.execute("SELECT name, balance FROM accounts WHERE type = ?", 'asset')
    liabilities = db.execute("SELECT name, balance FROM accounts WHERE type = ?", 'liability')

    asset_total = sum(float(a["balance"]) for a in assets)
    liability_total = sum(float(l["balance"]) for l in liabilities)

    return asset_total - liability_total


@app.route("/")
def index():
    networth = calculate_networth()

    assets = db.execute("SELECT name, balance FROM accounts WHERE type = ?", 'asset')
    liabilities = db.execute("SELECT name, balance FROM accounts WHERE type = ?", 'liability')

    return render_template("index.html", assets=assets, liabilities=liabilities, networth=networth)

@app.route("/login")
def login():
    return render_template("login.html")

@app.route("/register")
def register():
    return render_template("register.html")

@app.route("/accounts")
def accounts():
    # Fetch all accounts for current user
    user_id = 1
    accounts = db.execute("SELECT * FROM accounts WHERE user_id = ?", user_id)

    return render_template("accounts.html", accounts=accounts)

@app.route("/account", methods=["GET", "POST"])
@app.route("/account/<int:account_id>", methods=["GET", "POST"])
def account(account_id=None):
    if account_id:
        # Edit existing account
        account = db.execute("SELECT * FROM accounts WHERE id = ?", account_id)
        if not account:
            return "Account not found", 404
        account = account[0]
    else:
        account = None

    if request.method == "POST":
        name = request.form.get("name")
        type = request.form.get("type")
        source_type = request.form.get("source_type")
        api_provider = request.form.get("api_provider")
        account_identifier = request.form.get("account_identifier")

        # Get balance for api and manual
        if source_type == "api":
            # Build temporary account dict to send
            tmp_account = {
                "api_provider": api_provider,
                "account_identifier": account_identifier
            }

            balance = get_balance_for_account(tmp_account)
        else:
            balance = request.form.get("balance")
            balance = float(balance) if balance else None

        if account_id:
            db.execute(
                """
                UPDATE accounts
                SET name=?, type=?, source_type=?, api_provider=?, account_identifier=?, balance=?
                WHERE id=?
                """,
                name, type, source_type, api_provider, account_identifier, balance, account_id
            )
        else:
            db.execute(
                """
                INSERT INTO accounts (user_id, name, type, source_type, api_provider, account_identifier, balance)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                1, name, type, source_type, api_provider, account_identifier, balance
            )
        return redirect("/accounts")
    
    return render_template("account_form.html", account=account)

@app.route("/delete/<int:account_id>", methods=["GET", "POST"])
def delete(account_id):
    db.execute(
        """
        DELETE FROM accounts
        WHERE id = ?
        """,
        account_id
    )

    return redirect("/accounts")

@app.route("/history")
def history():
    return render_template("history.html")

