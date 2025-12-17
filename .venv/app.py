from cs50 import SQL

from flask import Flask, request, redirect, render_template, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash

from helper_functions import usd, apology, login_required
from api_handlers import get_balance_for_account
from charts import networth_pie_chart, networth_line_chart

# Configure application
app = Flask(__name__)

# Jinja filters
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure cs50 library to use SQlite database
db = SQL("sqlite:///tracker.db")

# Networth calculation
def calculate_networth():
    user_id = session["user_id"]
    # Get all accounts
    accounts = db.execute("SELECT * FROM accounts WHERE user_id = ?", user_id)

    for acct in accounts:
        if acct["source_type"] == "api":
            latest = get_balance_for_account(acct)

            if latest is not None:
                db.execute("UPDATE accounts SET balance = ? WHERE id = ? AND user_id = ?", latest, acct["id"], user_id)

    # After updating balances, recompute totals
    assets = db.execute("SELECT name, balance FROM accounts WHERE type = ? AND user_id = ?", 'asset', user_id)
    liabilities = db.execute("SELECT name, balance FROM accounts WHERE type = ? AND user_id = ?", 'liability', user_id)

    asset_total = sum(float(a["balance"]) or 0 for a in assets)
    liability_total = sum(float(l["balance"]) or 0 for l in liabilities)

    networth = asset_total - abs(liability_total)

    # update history 
    db.execute("INSERT INTO balances (user_id, value, assets, liabilities) VALUES (?, ?, ?, ?)", user_id, networth, asset_total, liability_total)

    return networth


@app.route("/update-networth", methods=["GET", "POST"])
def update_networth():
    user_id = session["user_id"]

    if request.method == "POST":
        # update all
        if request.form.get("update_all"):
            for key, value in request.form.items():
                if key.startswith("account_"):
                    account_id = key.replace("account_", "")
                    db.execute("UPDATE accounts SET balance = ?, last_updated = CURRENT_TIMESTAMP WHERE id = ? AND user_id = ?", float(value), account_id, user_id)
        # update a single account
        elif request.form.get("account_id"):
            account_id = request.form.get("account_id")
            balance = request.form.get("balance")

            db.execute("UPDATE accounts SET balance = ?, last_updated = CURRENT_TIMESTAMP WHERE id = ? AND user_id = ?", float(balance), account_id, user_id)
            
        return redirect("/")

    accounts = db.execute("SELECT id, name, balance FROM accounts WHERE user_id = ? ORDER BY name", user_id)

    return render_template("update_networth.html", accounts=accounts)


@app.route("/")
@login_required
def index():
    user_id = session["user_id"]

    networth = calculate_networth()

    assets = db.execute("SELECT name, balance, strftime('%m-%d at %H:%M', last_updated) AS last_updated FROM accounts WHERE type = ? AND user_id = ?", 'asset', user_id)
    liabilities = db.execute("SELECT name, balance, strftime('%m-%d at %H:%M', last_updated) AS last_updated FROM accounts WHERE type = ? AND user_id = ?", 'liability', user_id)

    asset_total = sum(a["balance"] or 0 for a in assets)
    liability_total = sum(abs(l["balance"]) or 0 for l in liabilities) # abs value pie chart does not allow negative integers

    # covers if user has no data
    show_pie = (asset_total > 0 or liability_total > 0)

    pie_chart = (networth_pie_chart(asset_total, liability_total) if show_pie else None)
    

    history = db.execute(
        """
        SELECT strftime('%Y-%m', timestamp) AS month, AVG(value) AS networth FROM balances
        WHERE user_id = ?
        GROUP BY month
        ORDER BY month
        """,
        user_id
    )

    months = [row["month"] for row in history if row["networth"] is not None]
    values = [row["networth"] for row in history if row["networth"] is not None]

    line_chart = networth_line_chart(months, values) if values[0] > 0 else None

    return render_template(
                            "index.html", 
                            pie_chart=pie_chart,
                            line_chart=line_chart,
                            assets=assets, 
                            asset_total=asset_total,
                            liabilities=liabilities,
                            liability_total=liability_total, 
                            networth=networth
                            )

@app.route("/login", methods=["GET", "POST"])
def login():
    # Forget any user_id
    session.clear()

    # User reached route via POST 
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("Input a username")
        elif not request.form.get("password"):
            return apology("Input a password")
        
        # Query database for username
        rows = db.execute("SELECT * from users WHERE username = ?", request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(
            rows[0]["hash"], request.form.get("password")
        ):
            return apology("Invalid user and/or password")
        
        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    return render_template("login.html")
    
@app.route("/logout")
def logout():
    session.clear()

    return redirect("/")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        first_name = request.form.get("first_name")
        last_name = request.form.get("last_name")
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        if not username:
            return apology("Must provider username")
        if not password:
            return apology("Must provide password")
        if password != confirmation:
            return apology("Passwords do not match")
        
        hash_password = generate_password_hash(password, method="scrypt", salt_length=16)

        try:
            db.execute("INSERT INTO users (username, hash, first_name, last_name) VALUES (?, ?, ?, ?)", username, hash_password, first_name, last_name)
        except ValueError:
            return apology("This username is taken")
        
        return redirect("/login")

    return render_template("register.html")

@app.route("/accounts")
@login_required
def accounts():
    # Fetch all accounts for current user
    user_id = session["user_id"]

    assets = db.execute("SELECT id, name, category, balance, datetime(last_updated, 'localtime') AS last_updated, url FROM accounts WHERE user_id = ? AND type = ?", user_id, "asset")
    liabilities = db.execute("SELECT id, name, category, balance, datetime(last_updated, 'localtime') AS last_updated, url FROM accounts WHERE user_id = ? AND type = ?", user_id, "liability")

    return render_template("accounts.html", assets=assets, liabilities=liabilities)

@app.route("/account", methods=["GET", "POST"])
@app.route("/account/<int:account_id>", methods=["GET", "POST"])
@login_required
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
        category = request.form.get("category")
        source_type = request.form.get("source_type")
        api_provider = request.form.get("api_provider")
        account_identifier = request.form.get("account_identifier")
        url = request.form.get("url")

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
                SET name=?, type=?, category=?, source_type=?, api_provider=?, account_identifier=?, balance=?, url=?
                WHERE id=?
                """,
                name, type, category, source_type, api_provider, account_identifier, balance, url, account_id
            )
        else:
            db.execute(
                """
                INSERT INTO accounts (user_id, name, type, category, source_type, api_provider, account_identifier, balance, url)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                1, name, type, category, source_type, api_provider, account_identifier, balance, url
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
@login_required
def history():
    user_id = session["user_id"]

    balances = db.execute(
        """
        SELECT * FROM balances WHERE user_id = ?;
        """, user_id
    )
    return render_template("history.html", balances=balances)

